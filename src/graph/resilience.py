
from itertools import combinations
import math

import networkx as nx

from src.graph.routing import create_graph
from src.graph.criticality import create_vulnerable_graph


def reachable_pairs(graph, original_nodes):
    """
    Return unordered origin-destination pairs that
    remain reachable in the modified graph.
    """
    reachable = set()

    for source, destination in combinations(original_nodes, 2):
        if (
            source in graph
            and destination in graph
            and nx.has_path(graph, source, destination)
        ):
            reachable.add((source, destination))

    return reachable


def calculate_resilience(original_graph, modified_graph):
    """
    Compare connectivity using the original graph's
    reachable origin-destination pairs.
    """
    nodes = sorted(original_graph.nodes)

    before = reachable_pairs(original_graph, nodes)
    after = reachable_pairs(modified_graph, nodes)

    if not before:
        return {
            "resilience_index": None,
            "reachable_before": 0,
            "reachable_after": 0,
            "lost_pairs": 0,
        }

    retained = before & after

    return {
        "resilience_index": len(retained) / len(before),
        "reachable_before": len(before),
        "reachable_after": len(retained),
        "lost_pairs": len(before - retained),
    }


def evaluate_edge_failure(graph, source, target):
    """Remove one road and measure network disruption."""
    if not graph.has_edge(source, target):
        raise ValueError(f"Road {source}-{target} not found")

    modified = graph.copy()
    modified.remove_edge(source, target)

    result = calculate_resilience(graph, modified)

    result["failed_edge"] = tuple(sorted((source, target)))
    result["components_after"] = nx.number_connected_components(
        modified
    )

    return result


def evaluate_node_failure(graph, node):
    """Remove one intersection and its connected roads."""
    if node not in graph:
        raise ValueError(f"Intersection {node} not found")

    modified = graph.copy()
    modified.remove_node(node)

    result = calculate_resilience(graph, modified)

    result["failed_node"] = node
    result["components_after"] = nx.number_connected_components(
        modified
    )

    return result


def rank_critical_edges(graph):
    """Rank road failures by lost reachable pairs."""
    results = []

    for source, target in graph.edges:
        result = evaluate_edge_failure(graph, source, target)
        results.append(result)

    return sorted(
        results,
        key=lambda item: (
            -item["lost_pairs"],
            item["failed_edge"]
        )
    )


def rank_critical_nodes(graph):
    """Rank intersection failures by lost reachable pairs."""
    results = []

    for node in graph.nodes:
        result = evaluate_node_failure(graph, node)
        results.append(result)

    return sorted(
        results,
        key=lambda item: (
            -item["lost_pairs"],
            item["failed_node"]
        )
    )


def print_report(graph):
    print("\nNETWORK BASELINE")
    print("Nodes:", graph.number_of_nodes())
    print("Roads:", graph.number_of_edges())

    print("\nEDGE FAILURE RANKING")
    for result in rank_critical_edges(graph)[:5]:
        print(
            f"{result['failed_edge']}: "
            f"R={result['resilience_index']:.4f}, "
            f"lost_pairs={result['lost_pairs']}"
        )

    print("\nNODE FAILURE RANKING")
    for result in rank_critical_nodes(graph)[:5]:
        print(
            f"{result['failed_node']}: "
            f"R={result['resilience_index']:.4f}, "
            f"lost_pairs={result['lost_pairs']}"
        )


if __name__ == "__main__":
    print("========== ORIGINAL ROAD NETWORK ==========")
    print_report(create_graph())

    print("\n========== VULNERABLE NETWORK ==========")
    print_report(create_vulnerable_graph())
