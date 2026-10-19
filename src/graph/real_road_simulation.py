
"""
Day 9: Real-world road closure simulation.

Loads Koramangala's OSM network, calculates a route,
simulates one directed road closure, and visualizes
the original and alternative routes.

All road closures in this module are simulated.
"""

from pathlib import Path
import math

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

from src.graph.routing import dijkstra_osm
from src.graph.directed_closure import (
    close_directed_edges,
    find_route_edges,
)


GRAPH_PATH = Path(
    "G:/Route-Resilience/data/raw/koramangala_roads.graphml"
)


def select_distant_nodes(graph):
    """
    Select geographically separated intersections from
    the largest strongly connected component.

    Strong connectivity means both endpoints can reach
    each other through permitted directed roads.
    """
    largest_component = max(
        nx.strongly_connected_components(graph),
        key=len,
    )

    nodes = list(largest_component)

    if len(nodes) < 2:
        raise ValueError(
            "Not enough connected intersections for routing."
        )

    # Use geographic corners as a simple demonstration.
    start = min(
        nodes,
        key=lambda n: (
            graph.nodes[n]["x"] + graph.nodes[n]["y"]
        ),
    )

    destination = max(
        nodes,
        key=lambda n: (
            graph.nodes[n]["x"] + graph.nodes[n]["y"]
        ),
    )

    if start == destination:
        raise ValueError(
            "Could not select distinct route endpoints."
        )

    return start, destination


def choose_road_to_close(graph, route):
    """
    Choose a road edge near the middle of the route.

    Avoids selecting the first or last edge so the
    disruption is easier to visualize.
    """
    route_edges = find_route_edges(graph, route)

    if not route_edges:
        raise ValueError(
            "The route must contain at least one edge."
        )

    middle_index = len(route_edges) // 2

    return route_edges[middle_index]


def run_simulation(graph, start, destination):
    """
    Calculate original route, simulate a directional
    road closure, and recalculate the route.
    """
    original_route, original_distance = dijkstra_osm(
        graph,
        start,
        destination,
        weight="length",
    )

    if not original_route:
        raise ValueError(
            "No original route exists between endpoints."
        )

    closed_edge = choose_road_to_close(
        graph, original_route
    )

    modified_graph = close_directed_edges(
        graph, [closed_edge]
    )

    alternative_route, alternative_distance = (
        dijkstra_osm(
            modified_graph,
            start,
            destination,
            weight="length",
        )
    )

    if math.isinf(alternative_distance):
        detour_percent = None
    elif original_distance == 0:
        detour_percent = 0.0
    else:
        detour_percent = (
            (alternative_distance - original_distance)
            / original_distance
        ) * 100

    return {
        "start": start,
        "destination": destination,
        "closed_edge": closed_edge,
        "original_route": original_route,
        "alternative_route": alternative_route,
        "original_distance": original_distance,
        "alternative_distance": alternative_distance,
        "detour_percent": detour_percent,
        "reachable_after": bool(alternative_route),
    }


def visualize_simulation(graph, result):
    """
    Plot the road network and both routes.

    Blue: original route
    Green: alternative route
    Red: selected closed road segment
    """
    fig, ax = ox.plot_graph(
        graph,
        node_size=0,
        edge_color="#B0B0B0",
        edge_linewidth=0.6,
        bgcolor="white",
        show=False,
        close=False,
    )

    ox.plot_graph_route(
        graph,
        result["original_route"],
        route_color="blue",
        route_linewidth=3,
        node_size=0,
        ax=ax,
        show=False,
        close=False,
    )

    if result["alternative_route"]:
        ox.plot_graph_route(
            graph,
            result["alternative_route"],
            route_color="green",
            route_linewidth=3,
            node_size=0,
            ax=ax,
            show=False,
            close=False,
        )

    u, v, key = result["closed_edge"]

    # Plot the exact closed road geometry when available.
    edge_data = graph[u][v][key]

    if "geometry" in edge_data:
        geometry = edge_data["geometry"]
        xs, ys = geometry.xy
    else:
        xs = [
            graph.nodes[u]["x"],
            graph.nodes[v]["x"],
        ]
        ys = [
            graph.nodes[u]["y"],
            graph.nodes[v]["y"],
        ]

    ax.plot(
        xs,
        ys,
        color="red",
        linewidth=5,
        solid_capstyle="round",
        zorder=10,
    )

    start = result["start"]
    destination = result["destination"]

    ax.scatter(
        graph.nodes[start]["x"],
        graph.nodes[start]["y"],
        color="blue",
        s=75,
        zorder=12,
        label="Start",
    )

    ax.scatter(
        graph.nodes[destination]["x"],
        graph.nodes[destination]["y"],
        color="black",
        s=75,
        zorder=12,
        label="Destination",
    )

    from matplotlib.lines import Line2D

    legend_items = [
        Line2D(
            [0], [0],
            color="blue", linewidth=3,
            label="Original route",
        ),
        Line2D(
            [0], [0],
            color="green", linewidth=3,
            label="Alternative route",
        ),
        Line2D(
            [0], [0],
            color="red", linewidth=4,
            label="Simulated closure",
        ),
    ]

    ax.legend(handles=legend_items, loc="upper right")
    ax.set_title(
        "Route Resilience - Koramangala Road Closure",
        fontsize=13,
    )

    plt.show()


def print_results(result):
    """Print a human-readable simulation summary."""
    print("\n========== ROUTE RESILIENCE ==========")
    print("Start node:", result["start"])
    print("Destination node:", result["destination"])
    print("Closed directed edge:", result["closed_edge"])

    print(
        "Original distance:",
        round(result["original_distance"], 2),
        "metres",
    )

    if result["reachable_after"]:
        print(
            "Alternative distance:",
            round(result["alternative_distance"], 2),
            "metres",
        )
        print(
            "Detour:",
            round(result["detour_percent"], 2),
            "%",
        )
    else:
        print("No alternative route available.")
        print("Destination became unreachable.")


def main():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"OSM graph not found: {GRAPH_PATH}"
        )

    graph = ox.load_graphml(GRAPH_PATH)

    print("Loaded Koramangala OSM graph")
    print("Nodes:", graph.number_of_nodes())
    print("Directed edges:", graph.number_of_edges())

    start, destination = select_distant_nodes(graph)

    result = run_simulation(
        graph, start, destination
    )

    print_results(result)
    visualize_simulation(graph, result)


if __name__ == "__main__":
    main()
