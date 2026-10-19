
import networkx as nx
import pytest

from src.graph.routing import create_graph
from src.graph.criticality import (
    create_vulnerable_graph,
    find_bridges,
    find_articulation_points,
    edge_betweenness,
    node_betweenness,
)


def test_original_graph_has_no_bridges():
    graph = create_graph()

    assert find_bridges(graph) == []


def test_original_graph_has_no_articulation_points():
    graph = create_graph()

    assert find_articulation_points(graph) == []


def test_vulnerable_graph_bridge():
    graph = create_vulnerable_graph()

    assert find_bridges(graph) == [("C", "D")]


def test_vulnerable_graph_articulation_points():
    graph = create_vulnerable_graph()

    assert find_articulation_points(graph) == ["C", "D"]


def test_bridge_removal_disconnects_graph():
    graph = create_vulnerable_graph()

    assert nx.is_connected(graph)

    graph.remove_edge("C", "D")

    assert not nx.is_connected(graph)
    assert nx.number_connected_components(graph) == 2


def test_edge_betweenness_scores():
    graph = create_vulnerable_graph()

    scores = dict(edge_betweenness(graph))

    assert scores[("C", "D")] == pytest.approx(0.6)


def test_node_betweenness_scores():
    graph = create_vulnerable_graph()

    scores = dict(node_betweenness(graph))

    assert scores["C"] == pytest.approx(0.6)
    assert scores["D"] == pytest.approx(0.6)


def test_original_graph_unchanged():
    graph = create_graph()

    find_bridges(graph)
    find_articulation_points(graph)
    edge_betweenness(graph)
    node_betweenness(graph)

    assert graph.number_of_nodes() == 10
    assert graph.number_of_edges() == 14
