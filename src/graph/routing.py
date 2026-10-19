
import heapq
import math
import networkx as nx
import matplotlib.pyplot as plt


ROADS = [
    ("A", "B", 4),
    ("B", "C", 3),
    ("C", "J", 5),
    ("A", "D", 2),
    ("B", "E", 6),
    ("C", "F", 2),
    ("D", "E", 3),
    ("E", "F", 4),
    ("F", "J", 2),
    ("D", "G", 5),
    ("E", "H", 2),
    ("F", "I", 3),
    ("G", "H", 4),
    ("H", "I", 2),
]

POSITIONS = {
    "A": (0, 2),
    "B": (2, 2),
    "C": (4, 2),
    "D": (0, 1),
    "E": (2, 1),
    "F": (4, 1),
    "G": (0, 0),
    "H": (2, 0),
    "I": (4, 0),
    "J": (5, 1),
}


def create_graph():
    graph = nx.Graph()

    for source, target, distance in ROADS:
        graph.add_edge(
            source,
            target,
            weight=distance
        )

    return graph


def dijkstra(graph, start, destination):
    """Return (path, cost), or ([], inf) if unreachable."""

    if start not in graph or destination not in graph:
        raise ValueError("Start or destination node not found")

    distances = {node: math.inf for node in graph.nodes}
    previous = {}

    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(
            priority_queue
        )

        if current_distance > distances[current_node]:
            continue

        if current_node == destination:
            break

        for neighbor, attributes in graph[current_node].items():
            weight = attributes["weight"]

            if weight < 0:
                raise ValueError("Dijkstra requires nonnegative weights")

            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbor)
                )

    if math.isinf(distances[destination]):
        return [], math.inf

    path = []
    node = destination

    while node != start:
        path.append(node)
        node = previous[node]

    path.append(start)
    path.reverse()

    return path, distances[destination]


def draw_graph(graph, path=None):
    plt.figure(figsize=(9, 5))

    nx.draw(
        graph,
        POSITIONS,
        with_labels=True,
        node_color="lightblue",
        node_size=750,
        font_weight="bold",
        edge_color="gray",
        width=2
    )

    labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(
        graph,
        POSITIONS,
        edge_labels=labels
    )

    if path and len(path) > 1:
        path_edges = list(zip(path[:-1], path[1:]))

        nx.draw_networkx_edges(
            graph,
            POSITIONS,
            edgelist=path_edges,
            edge_color="green",
            width=4
        )

    plt.title("Route Resilience - Synthetic Road Network")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    graph = create_graph()

    start = "A"
    destination = "I"

    path, distance = dijkstra(graph, start, destination)

    print("Shortest route:", " -> ".join(path))
    print("Total distance:", distance)

    draw_graph(graph, path)
