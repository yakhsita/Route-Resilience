
import pytest

from src.graph.routing import create_graph
from src.graph.criticality import create_vulnerable_graph
from src.graph.resilience import (
    calculate_resilience,
    evaluate_edge_failure,
    evaluate_node_failure,
    rank_critical_edges,
    rank_critical_nodes,
)


def test_no_failure():
    graph = create_graph()
    result = calculate_resilience(graph, graph)

    assert result["resilience_index"] == 1.0
    assert result["reachable_before"] == 45
    assert result["lost_pairs"] == 0


def test_original_network_edge_failure():
    graph = create_graph()
    result = evaluate_edge_failure(graph, "H", "I")

    assert result["resilience_index"] == 1.0
    assert result["lost_pairs"] == 0


def test_bridge_failure():
    graph = create_vulnerable_graph()
    result = evaluate_edge_failure(graph, "C", "D")

    assert result["resilience_index"] == pytest.approx(0.4)
    assert result["reachable_before"] == 15
    assert result["reachable_after"] == 6
    assert result["lost_pairs"] == 9
    assert result["components_after"] == 2


def test_articulation_point_failure():
    graph = create_vulnerable_graph()
    result = evaluate_node_failure(graph, "C")

    assert result["resilience_index"] == pytest.approx(4 / 15)
    assert result["lost_pairs"] == 11


def test_critical_edge_ranking():
    graph = create_vulnerable_graph()
    results = rank_critical_edges(graph)

    assert results[0]["failed_edge"] == ("C", "D")
    assert results[0]["lost_pairs"] == 9


def test_critical_node_ranking():
    graph = create_vulnerable_graph()
    results = rank_critical_nodes(graph)

    assert {results[0]["failed_node"],
            results[1]["failed_node"]} == {"C", "D"}


def test_original_graph_is_not_modified():
    graph = create_vulnerable_graph()

    evaluate_edge_failure(graph, "C", "D")
    evaluate_node_failure(graph, "C")

    assert graph.number_of_nodes() == 6
    assert graph.number_of_edges() == 7
