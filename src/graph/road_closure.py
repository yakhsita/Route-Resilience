
import math

from src.graph.routing import create_graph, dijkstra


def simulate_closure(graph, start, destination, closed_roads):
    """
    Simulate road closures without modifying the original graph.

    closed_roads: list of tuples, e.g. [("D", "E")]
    """
    updated_graph = graph.copy()

    for source, target in closed_roads:
        if not updated_graph.has_edge(source, target):
            raise ValueError(
                f"Road {source}-{target} does not exist"
            )

        updated_graph.remove_edge(source, target)

    path, distance = dijkstra(
        updated_graph, start, destination
    )

    return updated_graph, path, distance


def calculate_detour(original_distance, new_distance):
    """Return percentage increase in route distance."""
    if original_distance == 0:
        return 0.0 if new_distance == 0 else math.inf

    if math.isinf(new_distance):
        return math.inf

    return (
        (new_distance - original_distance)
        / original_distance
    ) * 100


if __name__ == "__main__":
    graph = create_graph()

    start = "A"
    destination = "I"

    original_path, original_distance = dijkstra(
        graph, start, destination
    )

    closed_roads = [("B", "E"), ("H", "I")]

    _, new_path, new_distance = simulate_closure(
        graph, start, destination, closed_roads
    )

    print("ORIGINAL NETWORK")
    print("Route:", " -> ".join(original_path))
    print("Distance:", original_distance)

    print("\nAFTER ROAD CLOSURE")
    print("Closed roads:", closed_roads)

    if new_path:
        print("New route:", " -> ".join(new_path))
        print("New distance:", new_distance)
        print(
            "Detour increase:",
            f"{calculate_detour(original_distance, new_distance):.2f}%"
        )
    else:
        print("No alternative route available!")
