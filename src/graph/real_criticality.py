
"""
Day 11: Sample-based road criticality on a real OSM graph.

All closures are hypothetical simulations.
Results apply to sampled journeys, not all city traffic.
"""

from pathlib import Path
import json
import math
import random

import networkx as nx
import osmnx as ox

from src.graph.routing import dijkstra_osm
from src.graph.directed_closure import (
    close_directed_edges,
    find_route_edges,
)
from collections import Counter

GRAPH_PATH = Path(
    "G:/Route-Resilience/data/raw/koramangala_roads.graphml"
)

REPORT_PATH = Path(
    "data/processed/koramangala_criticality.json"
)


def sample_od_pairs(graph, count=20, seed=42):
    """
    Sample reproducible directed journeys from the
    largest strongly connected component.
    """
    if count < 1:
        raise ValueError("count must be positive")

    components = nx.strongly_connected_components(graph)
    nodes = sorted(max(components, key=len))

    if len(nodes) < 2:
        raise ValueError("Need at least two connected nodes")

    rng = random.Random(seed)
    maximum = len(nodes) * (len(nodes) - 1)

    if count > maximum:
        raise ValueError("Too many unique OD pairs requested")

    pairs = set()

    while len(pairs) < count:
        start, end = rng.sample(nodes, 2)
        pairs.add((start, end))

    return sorted(pairs)



def prepare_journeys(graph, od_pairs):
    """
    Calculate baseline journeys and count how often
    each exact directed edge appears on their routes.
    """
    journeys = []
    edge_usage = Counter()

    for start, destination in od_pairs:
        route, distance = dijkstra_osm(
            graph,
            start,
            destination,
            weight="length",
        )

        if not route or not math.isfinite(distance):
            continue

        journeys.append({
            "start": start,
            "destination": destination,
            "baseline_distance": distance,
        })

        route_edges = find_route_edges(graph, route)
        edge_usage.update(route_edges)

    candidates = [
        edge
        for edge, frequency in sorted(
            edge_usage.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )
    ]

    return journeys, candidates


def evaluate_candidate(graph, journeys, closed_edge):
    """
    Evaluate one hypothetical directed edge closure
    against all baseline-reachable sampled journeys.
    """
    modified = close_directed_edges(
        graph, [closed_edge]
    )

    lost_journeys = 0
    total_extra_metres = 0.0
    reachable_detours = []

    for journey in journeys:
        _, new_distance = dijkstra_osm(
            modified,
            journey["start"],
            journey["destination"],
            weight="length",
        )

        if math.isinf(new_distance):
            lost_journeys += 1
            continue

        extra = max(
            0.0,
            new_distance - journey["baseline_distance"],
        )

        total_extra_metres += extra

        if journey["baseline_distance"] > 0:
            reachable_detours.append(
                100 * extra / journey["baseline_distance"]
            )

    return {
        "edge": list(closed_edge),
        "journeys_evaluated": len(journeys),
        "lost_journeys": lost_journeys,
        "connectivity_loss_percent": (
            100 * lost_journeys / len(journeys)
            if journeys else 0.0
        ),
        "total_extra_metres": round(
            total_extra_metres, 2
        ),
        "average_detour_percent": round(
            sum(reachable_detours) / len(reachable_detours),
            2,
        ) if reachable_detours else None,
    }


def rank_critical_roads(
    graph, od_pairs, max_candidates=30
):
    """
    Rank candidate directed edges by:
    1. Lost sampled journeys (descending)
    2. Total additional distance (descending)

    Candidate edges come from baseline shortest routes.
    """
    if max_candidates < 1:
        raise ValueError("max_candidates must be positive")

    journeys, candidates = prepare_journeys(
        graph, od_pairs
    )

    # Evaluate the most frequently used directed edges.
    selected = candidates[:max_candidates]

    results = [
        evaluate_candidate(graph, journeys, edge)
        for edge in selected
    ]

    results.sort(
        key=lambda result: (
            -result["lost_journeys"],
            -result["total_extra_metres"],
            tuple(result["edge"]),
        )
    )

    return results


def save_report(results, path=REPORT_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "analysis": "sampled_directed_edge_criticality",
                "closure_type": "hypothetical",
                "results": results,
            },
            file,
            indent=2,
        )

    return path


def main():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(GRAPH_PATH)

    graph = ox.load_graphml(GRAPH_PATH)

    print("Koramangala network loaded")
    print("Nodes:", graph.number_of_nodes())
    print("Directed edges:", graph.number_of_edges())

    pairs = sample_od_pairs(
        graph, count=100, seed=42
    )

    print("Sampled journeys:", len(pairs))

    results = rank_critical_roads(
        graph,
        pairs,
        max_candidates=50,
    )

    print("\n===== TOP 10 CRITICAL ROAD EDGES =====")

    for rank, item in enumerate(results[:10], 1):
        print(f"\n{rank}. Edge: {item['edge']}")
        print("Lost journeys:", item["lost_journeys"])
        print(
            "Connectivity loss:",
            f"{item['connectivity_loss_percent']:.2f}%"
        )
        print(
            "Total extra distance:",
            item["total_extra_metres"],
            "m",
        )
        print(
            "Average reachable detour:",
            item["average_detour_percent"],
            "%",
        )

    output = save_report(results)
    print("\nReport saved to:", output)


if __name__ == "__main__":
    main()
