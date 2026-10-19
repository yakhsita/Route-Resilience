
from pathlib import Path
import math

import networkx as nx
import osmnx as ox

from src.graph.routing import dijkstra_osm


# Keep your confirmed Windows path.
OSM_GRAPH_PATH = Path(
    "G:/Route-Resilience/data/raw/koramangala_roads.graphml"
)



def create_structural_graph(osm_graph):
    """
    Build an undirected structural graph from OSM roads.

    - Keeps the original node IDs and coordinates.
    - Collapses opposite-direction and parallel connections.
    - Uses the shortest length when multiple edges exist.
    - Does not modify the original OSM graph.
    """
    import networkx as nx

    structural = nx.Graph()

    for node, attributes in osm_graph.nodes(data=True):
        structural.add_node(
            node,
            **attributes
        )

    for u, v, key, attributes in osm_graph.edges(
        keys=True, data=True
    ):
        length = attributes["length"]

        if structural.has_edge(u, v):
            structural[u][v]["weight"] = min(
                structural[u][v]["weight"],
                length,
            )
        else:
            structural.add_edge(
                u,
                v,
                weight=length,
            )

    structural.graph["source"] = "OSM structural projection"
    structural.graph["coordinate_system"] = str(
        osm_graph.graph.get("crs", "unknown")
    )

    return structural



def analyze_structural_network(osm_graph):
    """
    Analyze physical connectivity using the
    undirected structural projection.
    """
    from src.graph.criticality import (
        find_bridges,
        find_articulation_points,
    )

    structural = create_structural_graph(osm_graph)

    bridges = find_bridges(structural)
    articulation_points = find_articulation_points(
        structural
    )

    print("\n========== STRUCTURAL ANALYSIS ==========")
    print("Nodes:", structural.number_of_nodes())
    print("Edges:", structural.number_of_edges())
    print("Bridges:", len(bridges))
    print("Articulation points:", len(articulation_points))

    print("\nFirst 10 bridges:")
    print(bridges[:10])

    print("\nFirst 10 articulation points:")
    print(articulation_points[:10])

    return structural, bridges, articulation_points



def load_osm_graph(path=OSM_GRAPH_PATH):
    """
    Load the real OSM road network.

    Keep its MultiDiGraph structure so that one-way
    streets and parallel edges are preserved.
    """
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"OSM road network not found: {path}"
        )

    graph = ox.load_graphml(path)

    validate_osm_graph(graph)

    return graph


def validate_osm_graph(graph):
    """
    Check that the graph has valid road lengths,
    geographic coordinates, and directed structure.
    """
    if not isinstance(graph, nx.MultiDiGraph):
        raise ValueError(
            "Expected a directed OSM MultiDiGraph"
        )

    if graph.number_of_nodes() == 0:
        raise ValueError("Road network is empty")

    for node, data in graph.nodes(data=True):
        latitude = data.get("y")
        longitude = data.get("x")

        if (
            not isinstance(latitude, (int, float))
            or not isinstance(longitude, (int, float))
            or not math.isfinite(latitude)
            or not math.isfinite(longitude)
            or not (-90 <= latitude <= 90)
            or not (-180 <= longitude <= 180)
        ):
            raise ValueError(
                f"Invalid coordinates at node {node}"
            )

    for u, v, key, data in graph.edges(
        keys=True, data=True
    ):
        length = data.get("length")

        if (
            not isinstance(length, (int, float))
            or not math.isfinite(length)
            or length <= 0
        ):
            raise ValueError(
                f"Invalid length on edge {(u, v, key)}"
            )

    return True


def nearest_intersection(graph, latitude, longitude):
    """
    Find the nearest mapped road-network node.

    For EPSG:4326 graphs, OSMnx expects longitude
    as X and latitude as Y.
    """
    return ox.distance.nearest_nodes(
        graph,
        X=longitude,
        Y=latitude,
    )


def shortest_route(graph, start_node, end_node):
    """
    Route using our custom Dijkstra implementation.

    Road length is measured in metres.
    """
    return dijkstra_osm(
        graph,
        start=start_node,
        destination=end_node,
        weight="length",
    )


def route_from_coordinates(
    graph,
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude,
):
    """
    Convert geographic coordinates into nearest
    graph nodes, then calculate the shortest route.
    """
    start_node = nearest_intersection(
        graph,
        start_latitude,
        start_longitude,
    )

    end_node = nearest_intersection(
        graph,
        end_latitude,
        end_longitude,
    )

    route, distance = shortest_route(
        graph,
        start_node,
        end_node,
    )

    return {
        "start_node": start_node,
        "end_node": end_node,
        "route": route,
        "distance_m": (
            None if math.isinf(distance)
            else round(distance, 2)
        ),
        "reachable": bool(route),
    }


def draw_route(graph, route):
    """Display the road network and calculated route."""
    if not route:
        print("No route to display.")
        return

    ox.plot_graph_route(
        graph,
        route,
        route_linewidth=3,
        node_size=0,
        bgcolor="white",
    )


if __name__ == "__main__":
    graph = load_osm_graph()

    print("========== REAL OSM NETWORK ==========")
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())
    print("Directed:", graph.is_directed())
    print("Multigraph:", graph.is_multigraph())
    print("CRS:", graph.graph.get("crs"))

    # Select two actual nodes from the same strongly
    # connected component to ensure a directed route exists.
    components = nx.strongly_connected_components(graph)
    largest_component = max(components, key=len)

    
    # Pick nodes near opposite geographic corners of
    # the largest strongly connected component.

    nodes = list(largest_component)

    start_node = min(
        nodes,
        key=lambda n: (
            graph.nodes[n]["x"] + graph.nodes[n]["y"]
        )
    )

    end_node = max(
        nodes,
        key=lambda n: (
            graph.nodes[n]["x"] + graph.nodes[n]["y"]
        )
    )

    route, distance = shortest_route(
        graph,
        start_node,
        end_node,
    )

    print("\n========== SHORTEST ROUTE ==========")
    print("Start node:", start_node)
    print("Destination node:", end_node)
    print("Route nodes:", len(route))
    print("Distance (metres):", round(distance, 2))

    print("\nDisplaying route...")
    draw_route(graph, route)
    analyze_structural_network(graph)
