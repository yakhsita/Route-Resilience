
"""
Day 10: Multiple directed road closure simulation.

Uses the real OSM road network and our custom Dijkstra.

All closures are simulated, not verified incidents.
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
from src.graph.real_road_simulation import (
    select_distant_nodes,
)

GRAPH_PATH = Path(
    "G:/Route-Resilience/data/raw/koramangala_roads.graphml"
)


def select_multiple_closures(graph, route, count=3):
    """
    Select evenly spaced directed edges along the route.

    For this demonstration, we deliberately close roads
    that belong to the original shortest path.
    """
    route_edges = find_route_edges(graph, route)

    if count < 1:
        raise ValueError("Closure count must be at least 1.")

    if count > len(route_edges):
        raise ValueError(
            "Closure count exceeds the number of route edges."
        )

    indices = [
        (i + 1) * len(route_edges) // (count + 1)
        for i in range(count)
    ]

    # Guarantee unique indices for short routes.
    selected = []
    used = set()

    for index in indices:
        while index in used and index < len(route_edges) - 1:
            index += 1

        if index not in used:
            selected.append(route_edges[index])
            used.add(index)

    if len(selected) != count:
        raise ValueError(
            "Could not select enough unique road segments."
        )

    return selected


def simulate_multiple_closures(
    graph, start, destination, closed_edges
):
    """
    Simulate multiple simultaneous directed road closures.
    """
    original_route, original_distance = dijkstra_osm(
        graph, start, destination, weight="length"
    )

    if not original_route:
        raise ValueError("No original route exists.")

    modified_graph = close_directed_edges(
        graph, closed_edges
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
        "closed_edges": list(closed_edges),
        "closure_count": len(closed_edges),
        "original_route": original_route,
        "alternative_route": alternative_route,
        "original_distance": original_distance,
        "alternative_distance": alternative_distance,
        "detour_percent": detour_percent,
        "reachable_after": bool(alternative_route),
    }


def compare_closure_counts(
    graph, start, destination, counts=(1, 2, 3)
):
    """
    Compare cumulative closure scenarios.

    Scenario 1: first selected road
    Scenario 2: first two selected roads
    Scenario 3: first three selected roads

    Each scenario includes all previous closures.
    """
    original_route, _ = dijkstra_osm(
        graph, start, destination, weight="length"
    )

    if not original_route:
        raise ValueError("No original route exists.")

    if not counts:
        return []

    if any(
        not isinstance(count, int) or count < 1
        for count in counts
    ):
        raise ValueError(
            "Closure counts must be positive integers."
        )

    # Select all candidate closures only once.
    maximum_count = max(counts)

    all_closures = select_multiple_closures(
        graph,
        original_route,
        count=maximum_count,
    )

    results = []

    for count in counts:
        closed_edges = all_closures[:count]

        result = simulate_multiple_closures(
            graph,
            start,
            destination,
            closed_edges,
        )

        results.append(result)

    return results


def print_comparison(results):
    print("\n====== MULTIPLE ROAD CLOSURES ======")

    for result in results:
        count = result["closure_count"]

        print(f"\nScenario: {count} road closure(s)")
        print("Closed edges:", result["closed_edges"])

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
            print("Destination is unreachable.")


def visualize_comparison(graph, results):
    """
    Display each closure scenario in a separate panel.

    Blue dashed: original route
    Green solid: alternative route
    Red: closed directed road segments
    """
    from matplotlib.lines import Line2D

    count = len(results)

    fig, axes = plt.subplots(
        1, count, figsize=(6 * count, 7)
    )

    if count == 1:
        axes = [axes]

    for ax, result in zip(axes, results):
        ox.plot_graph(
            graph,
            ax=ax,
            node_size=0,
            edge_color="#B5B5B5",
            edge_linewidth=0.5,
            bgcolor="white",
            show=False,
            close=False,
        )

        # Original route
        ox.plot_graph_route(
            graph,
            result["original_route"],
            route_color="blue",
            route_linewidth=2.5,
            node_size=0,
            ax=ax,
            show=False,
            close=False,
        )

        # Alternative route
        if result["alternative_route"]:
            ox.plot_graph_route(
                graph,
                result["alternative_route"],
                route_color="green",
                route_linewidth=2.5,
                node_size=0,
                ax=ax,
                show=False,
                close=False,
            )

        # Draw every simulated closure.
        for u, v, key in result["closed_edges"]:
            data = graph[u][v][key]

            if "geometry" in data:
                xs, ys = data["geometry"].xy
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
                xs, ys,
                color="red",
                linewidth=5,
                zorder=10,
                solid_capstyle="round",
            )

        if result["reachable_after"]:
            impact = (
                f"+{result['detour_percent']:.2f}%"
            )
        else:
            impact = "UNREACHABLE"

        ax.set_title(
            f"{result['closure_count']} closure(s)\n"
            f"Impact: {impact}",
            fontsize=12,
        )

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
            label="Closed road",
        ),
    ]

    fig.legend(
        handles=legend_items,
        loc="lower center",
        ncol=3,
    )

    fig.suptitle(
        "Route Resilience - Multiple Road Closures",
        fontsize=16,
    )

    plt.tight_layout(rect=[0, 0.07, 1, 0.94])
    plt.show()


def main():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"Graph file not found: {GRAPH_PATH}"
        )

    graph = ox.load_graphml(GRAPH_PATH)

    print("Loaded Koramangala OSM graph")
    print("Nodes:", graph.number_of_nodes())
    print("Directed edges:", graph.number_of_edges())

    start, destination = select_distant_nodes(graph)

    results = compare_closure_counts(
        graph,
        start,
        destination,
        counts=(1, 2, 3),
    )

    print_comparison(results)
    visualize_comparison(graph, results)


if __name__ == "__main__":
    main()
