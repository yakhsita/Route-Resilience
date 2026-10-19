
import math

import networkx as nx
import pytest

from src.graph.real_road_simulation import (
    select_distant_nodes,
    choose_road_to_close,
    run_simulation,
)


@pytest.fixture
def sample_graph():
    graph = nx.MultiDiGraph()
    graph.graph["crs"] = "epsg:4326"

    coordinates = {
        "A": (77.620, 12.930),
        "B": (77.621, 12.930),
        "C": (77.622, 12.930),
        "D": (77.621, 12.931),
    }

    for node, (x, y) in coordinates.items():
        graph.add_node(node, x=x, y=y)

    graph.add_edge("A", "B", length=100)
    graph.add_edge("B", "C", length=100)
    graph.add_edge("A", "D", length=150)
    graph.add_edge("D", "C", length=150)

    # Reverse links make all nodes strongly connected.
    graph.add_edge("B", "A", length=100)
    graph.add_edge("C", "B", length=100)
    graph.add_edge("D", "A", length=150)
    graph.add_edge("C", "D", length=150)

    return graph


def test_distant_nodes_are_distinct(sample_graph):
    start, end = select_distant_nodes(sample_graph)

    assert start != end


def test_distant_nodes_are_in_graph(sample_graph):
    start, end = select_distant_nodes(sample_graph)

    assert start in sample_graph
    assert end in sample_graph


def test_closure_edge_is_on_route(sample_graph):
    route = ["A", "B", "C"]

    edge = choose_road_to_close(
        sample_graph, route
    )

    assert edge[:2] in [
        ("A", "B"),
        ("B", "C"),
    ]


def test_original_route(sample_graph):
    result = run_simulation(
        sample_graph, "A", "C"
    )

    assert result["original_route"] == [
        "A", "B", "C"
    ]
    assert result["original_distance"] == 200


def test_detour_after_closure(sample_graph):
    result = run_simulation(
        sample_graph, "A", "C"
    )

    assert result["alternative_route"] == [
        "A", "D", "C"
    ]
    assert result["alternative_distance"] == 300
    assert result["detour_percent"] == pytest.approx(50)


def test_original_graph_unchanged(sample_graph):
    before = sample_graph.number_of_edges()

    run_simulation(sample_graph, "A", "C")

    assert sample_graph.number_of_edges() == before


def test_closed_edge_exists(sample_graph):
    result = run_simulation(
        sample_graph, "A", "C"
    )

    u, v, key = result["closed_edge"]

    assert sample_graph.has_edge(u, v, key)


def test_no_alternative_route():
    graph = nx.MultiDiGraph()

    graph.add_edge("A", "B", length=10)
    graph.add_edge("B", "C", length=10)

    result = run_simulation(graph, "A", "C")

    assert result["reachable_after"] is False
    assert result["alternative_route"] == []
    assert math.isinf(
        result["alternative_distance"]
    )
