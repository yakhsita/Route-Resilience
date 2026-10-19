
import json

import networkx as nx
import pytest

from src.graph.criticality_heatmap import (
    load_criticality_report,
    edge_coordinates,
    prepare_heatmap_data,
    draw_heatmap,
)


@pytest.fixture
def graph():
    network = nx.MultiDiGraph()
    network.graph["crs"] = "epsg:4326"

    network.add_node("A", x=77.62, y=12.93)
    network.add_node("B", x=77.63, y=12.93)
    network.add_node("C", x=77.64, y=12.94)

    network.add_edge(
        "A", "B", key=0, length=100
    )
    network.add_edge(
        "B", "C", key=0, length=120
    )

    return network


@pytest.fixture
def results():
    return [
        {
            "edge": ["A", "B", 0],
            "lost_journeys": 0,
            "total_extra_metres": 10,
        },
        {
            "edge": ["B", "C", 0],
            "lost_journeys": 2,
            "total_extra_metres": 100,
        },
    ]


def test_load_report(tmp_path):
    path = tmp_path / "report.json"

    path.write_text(
        json.dumps({
            "analysis": "sampled_directed_edge_criticality",
            "results": [],
        }),
        encoding="utf-8",
    )

    assert load_criticality_report(path) == []


def test_missing_report(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_criticality_report(
            tmp_path / "missing.json"
        )


def test_edge_coordinates(graph):
    coordinates = edge_coordinates(
        graph, "A", "B", 0
    )

    assert len(coordinates) == 2
    assert coordinates[0] == (77.62, 12.93)


def test_prepare_heatmap_data(graph, results):
    segments, scores, edge_ids = (
        prepare_heatmap_data(graph, results)
    )

    assert len(segments) == 2
    assert len(scores) == 2
    assert len(edge_ids) == 2


def test_higher_impact_higher_score(graph, results):
    _, scores, edge_ids = prepare_heatmap_data(
        graph, results
    )

    score_map = dict(zip(edge_ids, scores))

    assert (
        score_map[("B", "C", 0)]
        > score_map[("A", "B", 0)]
    )


def test_missing_edge_rejected(graph, results):
    results[0]["edge"] = ["X", "Y", 0]

    with pytest.raises(ValueError):
        prepare_heatmap_data(graph, results)


def test_empty_results(graph):
    segments, scores, edge_ids = (
        prepare_heatmap_data(graph, [])
    )

    assert segments == []
    assert scores == []
    assert edge_ids == []


def test_heatmap_saved(graph, results, tmp_path):
    output = tmp_path / "heatmap.png"

    saved = draw_heatmap(
        graph,
        results,
        output_path=output,
        show=False,
    )

    assert saved.exists()
    assert saved.stat().st_size > 0
