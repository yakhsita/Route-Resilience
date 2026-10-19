
import pytest
import networkx as nx

from src.graph.routing import create_graph
from src.graph.graph_io import (
    validate_graph,
    graph_to_dict,
    graph_from_dict,
    save_graph,
    load_graph,
)


def test_valid_synthetic_graph():
    assert validate_graph(create_graph()) is True


def test_graph_round_trip(tmp_path):
    original = create_graph()
    filepath = tmp_path / "network.json"

    save_graph(original, filepath)
    imported = load_graph(filepath)

    assert set(imported.nodes) == set(original.nodes)
    assert imported.number_of_edges() == original.number_of_edges()

    for u, v, data in original.edges(data=True):
        assert imported[u][v]["weight"] == data["weight"]


def test_graph_coordinates_preserved():
    graph = nx.Graph()
    graph.add_node("A", x=10, y=20)
    graph.add_node("B", x=40, y=50)
    graph.add_edge("A", "B", weight=5)

    restored = graph_from_dict(graph_to_dict(graph))

    assert restored.nodes["A"]["x"] == 10
    assert restored.nodes["A"]["y"] == 20


def test_missing_node_rejected():
    data = graph_to_dict(create_graph())
    data["edges"][0]["source"] = "MISSING"

    with pytest.raises(ValueError):
        graph_from_dict(data)


def test_duplicate_road_rejected():
    data = graph_to_dict(create_graph())
    data["edges"].append(data["edges"][0].copy())

    with pytest.raises(ValueError):
        graph_from_dict(data)


def test_negative_weight_rejected():
    graph = create_graph()
    graph["A"]["B"]["weight"] = -4

    with pytest.raises(ValueError):
        validate_graph(graph)


def test_zero_weight_rejected():
    graph = create_graph()
    graph["A"]["B"]["weight"] = 0

    with pytest.raises(ValueError):
        validate_graph(graph)


def test_missing_weight_rejected():
    graph = create_graph()
    del graph["A"]["B"]["weight"]

    with pytest.raises(ValueError):
        validate_graph(graph)


def test_invalid_coordinate_rejected():
    graph = nx.Graph()
    graph.add_node("A", x=10)
    graph.add_node("B")
    graph.add_edge("A", "B", weight=2)

    with pytest.raises(ValueError):
        validate_graph(graph)


def test_duplicate_node_rejected():
    data = graph_to_dict(create_graph())
    data["nodes"].append(data["nodes"][0].copy())

    with pytest.raises(ValueError):
        graph_from_dict(data)
