
import pytest
import networkx as nx

from src.graph.directed_closure import (
    close_directed_edges,
    simulate_directed_closure,
    find_route_edges,
)


def make_test_graph():
    graph = nx.MultiDiGraph()

    # Both travel directions exist.
    graph.add_edge("A", "B", key=0, length=5)
    graph.add_edge("B", "A", key=0, length=5)

    # Alternative route from A to B.
    graph.add_edge("A", "C", key=0, length=4)
    graph.add_edge("C", "B", key=0, length=4)

    return graph


def test_one_direction_closure():
    graph = make_test_graph()

    updated = close_directed_edges(
        graph, [("A", "B", 0)]
    )

    assert not updated.has_edge("A", "B", 0)
    assert updated.has_edge("B", "A", 0)


def test_reverse_route_still_works():
    graph = make_test_graph()

    updated = close_directed_edges(
        graph, [("A", "B", 0)]
    )

    result = simulate_directed_closure(
        updated, "B", "A", []
    )

    assert result["new_route"] == ["B", "A"]
    assert result["new_distance"] == 5


def test_detour_after_closure():
    graph = make_test_graph()

    result = simulate_directed_closure(
        graph,
        "A",
        "B",
        [("A", "B", 0)],
    )

    assert result["original_distance"] == 5
    assert result["new_distance"] == 8
    assert result["detour_percent"] == 60.0


def test_original_graph_preserved():
    graph = make_test_graph()

    close_directed_edges(
        graph, [("A", "B", 0)]
    )

    assert graph.has_edge("A", "B", 0)


def test_invalid_edge_rejected():
    graph = make_test_graph()

    with pytest.raises(ValueError):
        close_directed_edges(
            graph, [("A", "Z", 0)]
        )


def test_exact_route_edges():
    graph = make_test_graph()

    edges = find_route_edges(
        graph, ["A", "B"]
    )

    assert edges == [("A", "B", 0)]


def test_parallel_edge_preserved():
    graph = make_test_graph()
    graph.add_edge("A", "B", key=1, length=7)

    updated = close_directed_edges(
        graph, [("A", "B", 0)]
    )

    assert updated.has_edge("A", "B", 1)
