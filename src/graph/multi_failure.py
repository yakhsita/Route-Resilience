
from itertools import combinations
from pathlib import Path
import json
import math

import networkx as nx

from src.graph.routing import create_graph, dijkstra
from src.graph.vulnerability import baseline_distances


def canonical_edge(u, v):
    """Consistent representation of undirected roads."""
    return tuple(sorted((u, v)))


def simulate_multiple_failures(
    graph,
    closed_roads,
    start="A",
    destination="I",
    baseline=None,
):
    """
    Simulate simultaneous road closures.

    The original graph is never modified.
    """
    if start not in graph or destination not in graph:
        raise ValueError("Invalid start or destination")

    closures = sorted({
        canonical_edge(u, v)
        for u, v in closed_roads
    })

    for u, v in closures:
        if not graph.has_edge(u, v):
            raise ValueError(f"Road {u}-{v} does not exist")

    if baseline is None:
        baseline = baseline_distances(graph)

    original_path, original_distance = dijkstra(
        graph, start, destination
    )

    modified = graph.copy()
    modified.remove_edges_from(closures)

    new_path, new_distance = dijkstra(
        modified, start, destination
    )

    # Calculate shortest distances in the modified network.
    updated = dict(
        nx.all_pairs_dijkstra_path_length(
            modified, weight="weight"
        )
    )

    lost_pairs = 0
    detours = []

    for (source, target), old_distance in baseline.items():
        distance = updated[source].get(target, math.inf)

        if math.isinf(distance):
            lost_pairs += 1
        elif old_distance > 0:
            detour_pct = (
                (distance - old_distance)
                / old_distance
            ) * 100

            detours.append(max(0.0, detour_pct))

    total_pairs = len(baseline)
    remaining_pairs = total_pairs - lost_pairs

    if math.isinf(new_distance):
        route_detour_pct = None
    elif original_distance == 0:
        route_detour_pct = 0.0
    else:
        route_detour_pct = (
            (new_distance - original_distance)
            / original_distance
        ) * 100

    return {
        "closed_roads": closures,
        "closure_count": len(closures),
        "origin": start,
        "destination": destination,
        "original_route": original_path,
        "original_distance": (
            None if math.isinf(original_distance)
            else original_distance
        ),
        "new_route": new_path,
        "new_distance": (
            None if math.isinf(new_distance)
            else new_distance
        ),
        "route_reachable": bool(new_path),
        "route_detour_pct": (
            None if route_detour_pct is None
            else round(route_detour_pct, 4)
        ),
        "reachable_before": total_pairs,
        "reachable_after": remaining_pairs,
        "lost_pairs": lost_pairs,
        "connectivity_loss_pct": (
            round(100 * lost_pairs / total_pairs, 4)
            if total_pairs else None
        ),
        "resilience_index": (
            round(remaining_pairs / total_pairs, 4)
            if total_pairs else None
        ),
        "average_detour_pct": (
            round(sum(detours) / len(detours), 4)
            if detours else None
        ),
        "maximum_detour_pct": (
            round(max(detours), 4)
            if detours else None
        ),
        "components_after": nx.number_connected_components(
            modified
        ),
    }


def find_worst_combinations(
    graph,
    failure_count=2,
    top_n=10,
    start="A",
    destination="I",
):
    """
    Examine every combination of exactly failure_count roads.

    Ranking:
      1. More unreachable OD pairs
      2. Larger average detour among reachable OD pairs
      3. Larger maximum detour
    """
    if failure_count < 1 or failure_count > graph.number_of_edges():
        raise ValueError("Invalid failure_count")

    if top_n < 1:
        raise ValueError("top_n must be positive")

    baseline = baseline_distances(graph)
    edges = sorted(
        canonical_edge(u, v)
        for u, v in graph.edges()
    )

    results = []

    for closed_roads in combinations(edges, failure_count):
        result = simulate_multiple_failures(
            graph,
            closed_roads,
            start=start,
            destination=destination,
            baseline=baseline,
        )
        results.append(result)

    results.sort(
        key=lambda item: (
            -item["lost_pairs"],
            -(item["average_detour_pct"] or 0),
            -(item["maximum_detour_pct"] or 0),
            item["closed_roads"],
        )
    )

    return results[:top_n]


def print_scenario(result):
    print("\nClosed roads:", result["closed_roads"])

    if result["route_reachable"]:
        print(
            "New route:",
            " -> ".join(result["new_route"])
        )
        print("Distance:", result["new_distance"])
        print(
            "A-to-I detour:",
            f"{result['route_detour_pct']:.2f}%"
        )
    else:
        print("No alternative route available!")

    print(
        "Network resilience:",
        result["resilience_index"]
    )
    print("Lost OD pairs:", result["lost_pairs"])
    print(
        "Connected components:",
        result["components_after"]
    )


if __name__ == "__main__":
    graph = create_graph()

    scenarios = [
        [("A", "D")],
        [("H", "I")],
        [("G", "H"), ("D", "E")],
        [("G", "H"), ("D", "E"), ("B", "C")],
        [
            ("G", "H"), ("D", "E"),
            ("B", "C"), ("H", "I")
        ],
        [
            ("G", "H"), ("D", "E"),
            ("B", "C"), ("H", "I"), ("E", "F")
        ],
    ]

    print("========== FAILURE SCENARIOS ==========")

    scenario_results = []

    for scenario in scenarios:
        result = simulate_multiple_failures(
            graph, scenario
        )
        scenario_results.append(result)
        print_scenario(result)

    print("\n========== WORST TWO-ROAD FAILURES ==========")

    worst = find_worst_combinations(
        graph,
        failure_count=2,
        top_n=5
    )

    for rank, result in enumerate(worst, 1):
        print(
            f"{rank}. {result['closed_roads']} | "
            f"Lost pairs: {result['lost_pairs']} | "
            f"Avg detour: {result['average_detour_pct']}%"
        )

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    report = {
        "network": "synthetic_10_node",
        "scenario_results": scenario_results,
        "worst_two_road_failures": worst,
        "data_source": "simulated",
    }

    output_path = output_dir / "multi_failure_report.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"\nReport saved to: {output_path}")
