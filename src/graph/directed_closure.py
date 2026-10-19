
import math

from src.graph.routing import dijkstra_osm


def close_directed_edges(graph, closed_edges):
    """
    Remove selected directed OSM edges.

    Each edge is identified by (u, v, key).
    The original graph is never modified.
    """
    updated = graph.copy()

    for u, v, key in closed_edges:
        if not updated.has_edge(u, v, key):
            raise ValueError(
                f"Road edge does not exist: {(u, v, key)}"
            )

        updated.remove_edge(u, v, key)

    return updated


def simulate_directed_closure(
    graph,
    start,
    destination,
    closed_edges,
):
    """
    Simulate closures and calculate rerouting.

    Uses our custom Dijkstra with road lengths.
    """
    original_route, original_distance = dijkstra_osm(
        graph,
        start,
        destination,
        weight="length",
    )

    updated = close_directed_edges(
        graph,
        closed_edges,
    )

    new_route, new_distance = dijkstra_osm(
        updated,
        start,
        destination,
        weight="length",
    )

    if math.isinf(original_distance):
        detour_percent = None
    elif math.isinf(new_distance):
        detour_percent = None
    elif original_distance == 0:
        detour_percent = 0.0
    else:
        detour_percent = (
            (new_distance - original_distance)
            / original_distance
        ) * 100

    return {
        "closed_edges": list(closed_edges),
        "original_route": original_route,
        "original_distance": (
            None if math.isinf(original_distance)
            else round(original_distance, 2)
        ),
        "new_route": new_route,
        "new_distance": (
            None if math.isinf(new_distance)
            else round(new_distance, 2)
        ),
        "detour_percent": (
            None if detour_percent is None
            else round(detour_percent, 2)
        ),
        "reachable_before": bool(original_route),
        "reachable_after": bool(new_route),
    }


def find_route_edges(graph, route):
    """
    Return exact (u, v, key) edge IDs for a route.

    For each consecutive node pair, select the
    available edge with minimum length.
    """
    selected = []

    for u, v in zip(route[:-1], route[1:]):
        edge_options = graph.get_edge_data(u, v)

        if not edge_options:
            raise ValueError(
                f"No directed edge from {u} to {v}"
            )

        key = min(
            edge_options,
            key=lambda k: edge_options[k]["length"],
        )

        selected.append((u, v, key))

    return selected
