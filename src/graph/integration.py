
import json
import math
from pathlib import Path

from src.graph.routing import create_graph, dijkstra
from src.graph.criticality import (
    find_bridges,
    find_articulation_points,
    edge_betweenness,
)
from src.graph.resilience import evaluate_edge_failure
from src.graph.vulnerability import rank_vulnerable_roads
from src.graph.multi_failure import simulate_multiple_failures
from src.graph.graph_io import (
    save_graph,
    load_graph,
    validate_graph,
)


def analyze_network(graph, start, destination,
                    closed_roads=None):
    """Run the graph-analysis pipeline on one road network."""
    validate_graph(graph)

    if closed_roads is None:
        closed_roads = []

    path, distance = dijkstra(graph, start, destination)

    bridges = find_bridges(graph)
    articulation_points = find_articulation_points(graph)

    vulnerabilities = rank_vulnerable_roads(graph)

    failure = simulate_multiple_failures(
        graph,
        closed_roads,
        start=start,
        destination=destination,
    )

    return {
        "network": {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
        },
        "routing": {
            "origin": start,
            "destination": destination,
            "path": path,
            "distance": (
                None if math.isinf(distance) else distance
            ),
        },
        "criticality": {
            "bridges": sorted(
                [sorted(edge) for edge in bridges]
            ),
            "articulation_points": sorted(
                articulation_points
            ),
            "edge_betweenness": [
                {
                    "road": list(edge),
                    "score": score,
                }
                for edge, score in edge_betweenness(graph)
            ],
        },
        "vulnerability": vulnerabilities,
        "failure_scenario": failure,
    }


if __name__ == "__main__":
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    # Step 1: Start with our existing synthetic graph.
    original = create_graph()

    # Step 2: Export it using the shared JSON schema.
    graph_path = save_graph(
        original,
        output_dir / "road_network.json",
        coordinate_system="pixel",
        source="synthetic",
    )

    # Step 3: Load the graph back from JSON.
    imported = load_graph(graph_path)

    # Step 4: Run all analysis on the imported graph.
    report = analyze_network(
        imported,
        start="A",
        destination="I",
        closed_roads=[("D", "E")],
    )

    # Step 5: Save the integrated report.
    report_path = output_dir / "integrated_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("========== INTEGRATION REPORT ==========")
    print("Nodes:", report["network"]["nodes"])
    print("Roads:", report["network"]["edges"])
    print("Route:", " -> ".join(report["routing"]["path"]))
    print("Distance:", report["routing"]["distance"])
    print("Bridges:", report["criticality"]["bridges"])
    print(
        "Articulation points:",
        report["criticality"]["articulation_points"],
    )
    print(
        "Most vulnerable road:",
        report["vulnerability"][0]["road"],
    )
    print(
        "After D-E closure:",
        report["failure_scenario"]["new_route"],
    )
    print(
        "New distance:",
        report["failure_scenario"]["new_distance"],
    )

    print("\nGraph saved to:", graph_path)
    print("Report saved to:", report_path)
