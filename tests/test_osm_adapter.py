
import math

import networkx as nx
import pytest

from src.graph.osm_adapter import (
    validate_osm_graph,
    shortest_route,
    route_from_coordinates,
    nearest_intersection,
)


@pytest.fixture
def sample_osm_graph():
    """Small directed road network resembling OSM data."""
    graph = nx.MultiDiGraph()
    graph.graph["crs"] = "epsg:4326"

    graph.add_node(
        1, x=77.6200, y=12.9300
    )
    graph.add_node(
        2, x=77.6210, y=12.9300
    )
    graph.add_node(
        3, x=77.6220, y=12.9300
    )
    graph.add_node(
        4, x=77.6210, y=12.9310
    )

    graph.add_edge(1, 2, key=0, length=100.0)
    graph.add_edge(2, 3, key=0, length=100.0)
    graph.add_edge(1, 3, key=0, length=350.0)
    graph.add_edge(3, 4, key=0, length=120.0)
    graph.add_edge(4, 1, key=0, length=130.0)

    return graph


def test_osm_graph_is_valid(sample_osm_graph):
    assert validate_osm_graph(sample_osm_graph) is True


def test_osm_graph_must_be_directed():
    graph = nx.Graph()
    graph.add_edge(1, 2, length=100)

    with pytest.raises((TypeError, ValueError)):
        validate_osm_graph(graph)


def test_osm_graph_missing_coordinates(sample_osm_graph):
    del sample_osm_graph.nodes[1]["x"]

    with pytest.raises((TypeError, ValueError)):
        validate_osm_graph(sample_osm_graph)


def test_osm_graph_invalid_length(sample_osm_graph):
    sample_osm_graph[1][2][0]["length"] = -100

    with pytest.raises((TypeError, ValueError)):
        validate_osm_graph(sample_osm_graph)


def test_osm_graph_missing_length(sample_osm_graph):
    del sample_osm_graph[1][2][0]["length"]

    with pytest.raises((TypeError, ValueError)):
        validate_osm_graph(sample_osm_graph)


def test_shortest_route(sample_osm_graph):
    path, distance = shortest_route(
        sample_osm_graph, 1, 3
    )

    assert path == [1, 2, 3]
    assert distance == pytest.approx(200.0)


def test_shortest_route_respects_direction(sample_osm_graph):
    path, distance = shortest_route(
        sample_osm_graph, 2, 1
    )

    assert path == [2, 3, 4, 1]
    assert distance == pytest.approx(350.0)


def test_shortest_route_same_node(sample_osm_graph):
    path, distance = shortest_route(
        sample_osm_graph, 1, 1
    )

    assert path == [1]
    assert distance == 0


def test_nearest_intersection(sample_osm_graph):
    node = nearest_intersection(
        sample_osm_graph,
        latitude=12.9300,
        longitude=77.6200,
    )

    assert node == 1


def test_unreachable_route(sample_osm_graph):
    sample_osm_graph.add_node(
        5, x=77.6250, y=12.9350
    )

    path, distance = shortest_route(
        sample_osm_graph, 1, 5
    )

    assert path == []
    assert math.isinf(distance)
