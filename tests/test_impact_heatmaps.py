
import json

import networkx as nx
import pytest

from src.graph.impact_heatmaps import (
    prepare_metric_data,
    draw_impact_heatmaps,
)


@pytest.fixture
def graph():
    g = nx.MultiDiGraph()
    g.graph["crs"] = "epsg:4326"

    g.add_node("A", x=77.62, y=12.93)
    g.add_node("B", x=77.63, y=12.93)
    g.add_node("C", x=77.64, y=12.94)

    g.add_edge("A", "B", key=0, length=100)
    g.add_edge("B", "C", key=0, length=120)

    return g


@pytest.fixture
def results():
    return [
        {
            "edge": ["A", "B", 0],
            "connectivity_loss_percent": 0,
            "total_extra_metres": 0,
        },
        {
            "edge": ["B", "C", 0],
            "connectivity_loss_percent": 20,
            "total_extra_metres": 250,
        },
    ]


def test_connectivity_values(graph, results):
    _, values, _ = prepare_metric_data(
        graph, results, "connectivity_loss_percent"
    )

    assert values == [0, 20]


def test_detour_values(graph, results):
    _, values, _ = prepare_metric_data(
        graph, results, "total_extra_metres"
    )

    assert values == [0, 250]


def test_same_impact_same_value(graph, results):
    results[1]["connectivity_loss_percent"] = 0

    _, values, _ = prepare_metric_data(
        graph, results, "connectivity_loss_percent"
    )

    assert values == [0, 0]


def test_invalid_metric(graph, results):
    with pytest.raises(ValueError):
        prepare_metric_data(
            graph, results, "fake_metric"
        )


def test_missing_edge(graph, results):
    results[0]["edge"] = ["X", "Y", 0]

    with pytest.raises(ValueError):
        prepare_metric_data(
            graph, results, "total_extra_metres"
        )


def test_negative_impact_rejected(graph, results):
    results[0]["total_extra_metres"] = -5

    with pytest.raises(ValueError):
        prepare_metric_data(
            graph, results, "total_extra_metres"
        )


def test_empty_results(graph):
    segments, values, edge_ids = prepare_metric_data(
        graph, [], "total_extra_metres"
    )

    assert segments == []
    assert values == []
    assert edge_ids == []


def test_heatmaps_saved(graph, results, tmp_path):
    output = tmp_path / "impact_maps.png"

    saved = draw_impact_heatmaps(
        graph,
        results,
        output_path=output,
        show=False,
    )

    assert saved.exists()
    assert saved.stat().st_size > 0
