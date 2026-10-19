
import math

import networkx as nx
import pytest

from src.graph.real_multi_closure import (
    select_multiple_closures,
    simulate_multiple_closures,
    compare_closure_counts,
)


@pytest.fixture
def sample_graph():
    graph = nx.MultiDiGraph()

    graph.add_edge("A", "B", length=2)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("C", "D", length=2)
    graph.add_edge("D", "E", length=2)

    graph.add_edge("A", "F", length=5)
    graph.add_edge("F", "E", length=5)

    return graph


def test_select_one_closure(sample_graph):
    route = ["A", "B", "C", "D", "E"]

    selected = select_multiple_closures(
        sample_graph, route, count=1
    )

    assert len(selected) == 1


def test_select_three_closures(sample_graph):
    route = ["A", "B", "C", "D", "E"]

    selected = select_multiple_closures(
        sample_graph, route, count=3
    )

    assert len(selected) == 3
    assert len(set(selected)) == 3


def test_invalid_closure_count(sample_graph):
    route = ["A", "B", "C", "D", "E"]

    with pytest.raises(ValueError):
        select_multiple_closures(
            sample_graph, route, count=0
        )


def test_excessive_closure_count(sample_graph):
    route = ["A", "B", "C", "D", "E"]

    with pytest.raises(ValueError):
        select_multiple_closures(
            sample_graph, route, count=10
        )


def test_multiple_closure_detour(sample_graph):
    closed = [
        ("B", "C", 0),
        ("C", "D", 0),
    ]

    result = simulate_multiple_closures(
        sample_graph, "A", "E", closed
    )

    assert result["original_distance"] == 8
    assert result["alternative_distance"] == 10
    assert result["detour_percent"] == pytest.approx(25)


def test_original_graph_preserved(sample_graph):
    before = sample_graph.number_of_edges()

    simulate_multiple_closures(
        sample_graph,
        "A",
        "E",
        [("B", "C", 0)],
    )

    assert sample_graph.number_of_edges() == before


def test_unreachable_after_multiple_closures():
    graph = nx.MultiDiGraph()

    graph.add_edge("A", "B", length=2)
    graph.add_edge("B", "C", length=2)

    result = simulate_multiple_closures(
        graph,
        "A",
        "C",
        [("A", "B", 0), ("B", "C", 0)],
    )

    assert result["reachable_after"] is False
    assert math.isinf(
        result["alternative_distance"]
    )


def test_compare_closure_counts(sample_graph):
    results = compare_closure_counts(
        sample_graph,
        "A",
        "E",
        counts=(1, 2, 3),
    )

    assert len(results) == 3
    assert [
        result["closure_count"]
        for result in results
    ] == [1, 2, 3]
