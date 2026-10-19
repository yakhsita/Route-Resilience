
import json
import math

import pytest

from src.graph.routing import create_graph
from src.graph.multi_failure import (
    simulate_multiple_failures,
    find_worst_combinations,
)


def test_no_closures():
    graph = create_graph()

    result = simulate_multiple_failures(graph, [])

    assert result["new_distance"] == 9
    assert result["lost_pairs"] == 0
    assert result["resilience_index"] == 1.0


def test_single_closure():
    graph = create_graph()

    result = simulate_multiple_failures(
        graph, [("A", "D")]
    )

    assert result["new_distance"] == 12
    assert result["route_detour_pct"] == pytest.approx(
        33.3333, abs=0.001
    )


def test_three_road_closures():
    graph = create_graph()

    result = simulate_multiple_failures(
        graph,
        [("G", "H"), ("D", "E"), ("B", "C")]
    )

    assert result["new_distance"] == 14
    assert result["route_reachable"] is True


def test_four_road_closures():
    graph = create_graph()

    result = simulate_multiple_failures(
        graph,
        [
            ("G", "H"), ("D", "E"),
            ("B", "C"), ("H", "I")
        ]
    )

    assert result["new_distance"] == 17
    assert result["route_detour_pct"] == pytest.approx(
        88.8889, abs=0.001
    )


def test_five_road_closures_disconnect_route():
    graph = create_graph()

    result = simulate_multiple_failures(
        graph,
        [
            ("G", "H"), ("D", "E"),
            ("B", "C"), ("H", "I"), ("E", "F")
        ]
    )

    assert result["route_reachable"] is False
    assert result["new_route"] == []
    assert result["new_distance"] is None
    assert result["route_detour_pct"] is None


def test_isolate_destination():
    graph = create_graph()

    result = simulate_multiple_failures(
        graph,
        [("F", "I"), ("H", "I")]
    )

    assert result["lost_pairs"] == 9
    assert result["resilience_index"] == 0.8
    assert result["components_after"] == 2


def test_original_graph_not_modified():
    graph = create_graph()
    original_edges = set(graph.edges())

    simulate_multiple_failures(
        graph, [("A", "D"), ("H", "I")]
    )

    assert set(graph.edges()) == original_edges


def test_invalid_road():
    graph = create_graph()

    with pytest.raises(ValueError):
        simulate_multiple_failures(
            graph, [("A", "Z")]
        )


def test_duplicate_closure_counted_once():
    graph = create_graph()

    result = simulate_multiple_failures(
        graph,
        [("A", "D"), ("D", "A")]
    )

    assert result["closure_count"] == 1


def test_worst_combinations():
    graph = create_graph()

    results = find_worst_combinations(
        graph, failure_count=2, top_n=5
    )

    assert len(results) == 5
    assert all(
        result["closure_count"] == 2
        for result in results
    )

    assert results[0]["lost_pairs"] >= results[-1]["lost_pairs"]


def test_json_serialization():
    graph = create_graph()

    result = simulate_multiple_failures(
        graph, [("D", "E")]
    )

    assert isinstance(json.dumps(result), str)
