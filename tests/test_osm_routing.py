
import math

import networkx as nx
import pytest

from src.graph.routing import dijkstra_osm
from src.graph.osm_adapter import create_structural_graph


def make_directed_graph():
    graph = nx.MultiDiGraph()

    graph.add_edge("A", "B", length=5)
    graph.add_edge("B", "C", length=3)
    graph.add_edge("A", "C", length=12)

    return graph


def test_custom_dijkstra_directed():
    graph = make_directed_graph()

    path, distance = dijkstra_osm(
        graph, "A", "C"
    )

    assert path == ["A", "B", "C"]
    assert distance == 8


def test_one_way_road():
    graph = make_directed_graph()

    path, distance = dijkstra_osm(
        graph, "C", "A"
    )

    assert path == []
    assert math.isinf(distance)


def test_parallel_roads():
    graph = make_directed_graph()
    graph.add_edge("A", "B", length=2)

    path, distance = dijkstra_osm(
        graph, "A", "C"
    )

    assert path == ["A", "B", "C"]
    assert distance == 5


def test_same_origin_destination():
    graph = make_directed_graph()

    path, distance = dijkstra_osm(
        graph, "A", "A"
    )

    assert path == ["A"]
    assert distance == 0


def test_invalid_node():
    graph = make_directed_graph()

    with pytest.raises(ValueError):
        dijkstra_osm(graph, "A", "Z")


def test_against_networkx():
    graph = make_directed_graph()

    _, distance = dijkstra_osm(
        graph, "A", "C"
    )

    expected = nx.shortest_path_length(
        graph, "A", "C", weight="length"
    )

    assert distance == pytest.approx(expected)


def test_structural_graph_undirected():
    graph = make_directed_graph()

    structural = create_structural_graph(graph)

    assert structural.is_directed() is False
    assert structural.number_of_nodes() == 3
    assert structural.has_edge("B", "A")


def test_structural_graph_minimum_weight():
    graph = make_directed_graph()
    graph.add_edge("A", "B", length=2)

    structural = create_structural_graph(graph)

    assert structural["A"]["B"]["weight"] == 2


def test_structural_graph_preserves_original():
    graph = make_directed_graph()
    original_edges = graph.number_of_edges()

    create_structural_graph(graph)

    assert graph.number_of_edges() == original_edges


def test_invalid_edge_length():
    graph = make_directed_graph()
    graph["A"]["B"][0]["length"] = -1

    with pytest.raises(ValueError):
        dijkstra_osm(graph, "A", "C")
