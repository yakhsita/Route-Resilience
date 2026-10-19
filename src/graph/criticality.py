
import networkx as nx

from src.graph.routing import create_graph


def find_bridges(graph):
    """
    Return roads whose removal increases
    the number of connected components.
    """
    return sorted(
        [tuple(sorted(edge)) for edge in nx.bridges(graph)]
    )


def find_articulation_points(graph):
    """
    Return intersections whose removal
    increases the number of connected components.
    """
    return sorted(nx.articulation_points(graph))


def edge_betweenness(graph):
    """
    Calculate weighted edge betweenness centrality.

    Higher score = edge appears on more shortest paths.
    """
    scores = nx.edge_betweenness_centrality(
        graph,
        weight="weight",
        normalized=True
    )

    results = [
        (tuple(sorted(edge)), round(score, 4))
        for edge, score in scores.items()
    ]

    return sorted(
        results,
        key=lambda item: (-item[1], item[0])
    )


def node_betweenness(graph):
    """
    Calculate weighted node betweenness centrality.
    """
    scores = nx.betweenness_centrality(
        graph,
        weight="weight",
        normalized=True
    )

    return sorted(
        [
            (node, round(score, 4))
            for node, score in scores.items()
        ],
        key=lambda item: (-item[1], item[0])
    )


def create_vulnerable_graph():
    """
    Two triangular regions joined by a single road.
    """
    graph = nx.Graph()

    roads = [
        ("A", "B", 2),
        ("B", "C", 2),
        ("A", "C", 3),
        ("C", "D", 5),
        ("D", "E", 2),
        ("E", "F", 2),
        ("D", "F", 3),
    ]

    for u, v, weight in roads:
        graph.add_edge(u, v, weight=weight)

    return graph


def analyze_graph(graph):
    print("\nNETWORK INFORMATION")
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())
    print(
        "Connected components:",
        nx.number_connected_components(graph)
    )

    print("\nBRIDGE ROADS")
    bridges = find_bridges(graph)
    print(bridges if bridges else "No bridges found")

    print("\nARTICULATION POINTS")
    points = find_articulation_points(graph)
    print(points if points else "No articulation points found")

    print("\nTOP 5 CRITICAL ROADS BY BETWENNESS")
    for edge, score in edge_betweenness(graph)[:5]:
        print(f"{edge}: {score:.4f}")

    print("\nTOP 5 INTERSECTIONS BY BETWENNESS")
    for node, score in node_betweenness(graph)[:5]:
        print(f"{node}: {score:.4f}")


if __name__ == "__main__":
    print("========== ORIGINAL ROAD NETWORK ==========")
    analyze_graph(create_graph())

    print("\n========== VULNERABLE ROAD NETWORK ==========")
    analyze_graph(create_vulnerable_graph())
