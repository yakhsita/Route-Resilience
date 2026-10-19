
import json

import networkx as nx
import pytest

from src.graph.real_criticality import (
    sample_od_pairs,
    prepare_journeys,
    evaluate_candidate,
    rank_critical_roads,
    save_report,
)


@pytest.fixture
def road_graph():
    graph = nx.MultiDiGraph()

    graph.add_edge("A", "B", length=2)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("A", "D", length=5)
    graph.add_edge("D", "C", length=5)

    # Reverse connections for strong connectivity.
    graph.add_edge("B", "A", length=2)
    graph.add_edge("C", "B", length=2)
    graph.add_edge("D", "A", length=5)
    graph.add_edge("C", "D", length=5)

    return graph


def test_sampling_reproducible(road_graph):
    first = sample_od_pairs(road_graph, 5, seed=42)
    second = sample_od_pairs(road_graph, 5, seed=42)

    assert first == second


def test_sampling_unique_pairs(road_graph):
    pairs = sample_od_pairs(road_graph, 6)

    assert len(pairs) == len(set(pairs))
    assert all(a != b for a, b in pairs)


def test_invalid_sample_count(road_graph):
    with pytest.raises(ValueError):
        sample_od_pairs(road_graph, 0)


def test_prepare_journeys(road_graph):
    journeys, candidates = prepare_journeys(
        road_graph, [("A", "C")]
    )

    assert len(journeys) == 1
    assert journeys[0]["baseline_distance"] == 4
    assert ("A", "B", 0) in candidates


def test_candidate_detour(road_graph):
    journeys, _ = prepare_journeys(
        road_graph, [("A", "C")]
    )

    result = evaluate_candidate(
        road_graph,
        journeys,
        ("A", "B", 0),
    )

    assert result["lost_journeys"] == 0
    assert result["total_extra_metres"] == 6
    assert result["average_detour_percent"] == 150


def test_candidate_disconnects_journey():
    graph = nx.MultiDiGraph()
    graph.add_edge("A", "B", length=2)
    graph.add_edge("B", "C", length=2)

    journeys, _ = prepare_journeys(
        graph, [("A", "C")]
    )

    result = evaluate_candidate(
        graph, journeys, ("B", "C", 0)
    )

    assert result["lost_journeys"] == 1
    assert result["connectivity_loss_percent"] == 100
    assert result["average_detour_percent"] is None


def test_ranking_results(road_graph):
    results = rank_critical_roads(
        road_graph, [("A", "C")], max_candidates=2
    )

    assert len(results) == 2
    assert all("lost_journeys" in r for r in results)


def test_original_graph_unchanged(road_graph):
    before = road_graph.number_of_edges()

    rank_critical_roads(
        road_graph, [("A", "C")], max_candidates=2
    )

    assert road_graph.number_of_edges() == before


def test_save_report(tmp_path):
    output = tmp_path / "criticality.json"

    save_report([], output)

    with output.open(encoding="utf-8") as file:
        data = json.load(file)

    assert data["closure_type"] == "hypothetical"
    assert data["results"] == []
