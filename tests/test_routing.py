
import math
import networkx as nx
import pytest

from src.graph.routing import create_graph, dijkstra


def test_graph_structure():
    graph = create_graph()

    assert graph.number_of_nodes() == 10
    assert graph.number_of_edges() == 14


def test_shortest_path():
    graph = create_graph()

    path, distance = dijkstra(graph, "A", "I")

    assert path == ["A", "D", "E", "H", "I"]
    assert distance == 9


def test_same_start_and_destination():
    graph = create_graph()

    path, distance = dijkstra(graph, "A", "A")

    assert path == ["A"]
    assert distance == 0


def test_disconnected_destination():
    graph = create_graph()
    graph.remove_edges_from(list(graph.edges("I")))

    path, distance = dijkstra(graph, "A", "I")

    assert path == []
    assert math.isinf(distance)


def test_invalid_node():
    graph = create_graph()

    with pytest.raises(ValueError):
        dijkstra(graph, "A", "Z")


def test_against_networkx():
    graph = create_graph()

    for start in graph.nodes:
        for destination in graph.nodes:
            _, distance = dijkstra(
                graph, start, destination
            )

            expected = nx.dijkstra_path_length(
                graph, start, destination, weight="weight"
            )

            assert distance == expected
