
import json
import math
from pathlib import Path

import networkx as nx


SCHEMA_VERSION = "1.0"


def validate_graph(graph):
    """Check whether a graph is suitable for our algorithms."""
    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Expected an undirected NetworkX graph")

    if graph.is_multigraph():
        raise ValueError("Parallel roads are not supported yet")

    if graph.number_of_nodes() == 0:
        raise ValueError("Graph must contain at least one node")

    for node in graph.nodes:
        if not isinstance(node, str) or not node:
            raise ValueError("Node IDs must be nonempty strings")

    for node, attributes in graph.nodes(data=True):
        has_x = "x" in attributes
        has_y = "y" in attributes

        if has_x != has_y:
            raise ValueError(
                f"Node {node}: x and y must be provided together"
            )

        if has_x:
            for coordinate in ("x", "y"):
                value = attributes[coordinate]
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                ):
                    raise ValueError(
                        f"Node {node}: invalid {coordinate}"
                    )

    for u, v, attributes in graph.edges(data=True):
        if u == v:
            raise ValueError("Self-loop roads are not supported")

        weight = attributes.get("weight")

        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or weight <= 0
        ):
            raise ValueError(
                f"Road {u}-{v} must have a positive finite weight"
            )

    return True


def graph_to_dict(graph, coordinate_system="pixel",
                  source="synthetic"):
    """Convert a validated graph into our JSON schema."""
    validate_graph(graph)

    if coordinate_system not in ("pixel", "EPSG:4326"):
        raise ValueError("Unsupported coordinate system")

    nodes = []

    for node, attributes in sorted(graph.nodes(data=True)):
        record = {"id": node}

        if "x" in attributes:
            record["x"] = attributes["x"]
            record["y"] = attributes["y"]

        nodes.append(record)

    edges = []

    for u, v, attributes in graph.edges(data=True):
        a, b = sorted((u, v))

        edges.append({
            "source": a,
            "target": b,
            "weight": attributes["weight"],
        })

    edges.sort(key=lambda edge: (
        edge["source"], edge["target"]
    ))

    return {
        "schema_version": SCHEMA_VERSION,
        "coordinate_system": coordinate_system,
        "source": source,
        "directed": False,
        "nodes": nodes,
        "edges": edges,
    }


def graph_from_dict(data):
    """Build a NetworkX graph from validated JSON data."""
    if not isinstance(data, dict):
        raise ValueError("Graph data must be an object")

    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported schema version")

    if data.get("directed") is not False:
        raise ValueError("Only undirected graphs are supported")

    if data.get("coordinate_system") not in (
        "pixel", "EPSG:4326"
    ):
        raise ValueError("Unsupported coordinate system")

    if not isinstance(data.get("nodes"), list):
        raise ValueError("Nodes must be a list")

    if not isinstance(data.get("edges"), list):
        raise ValueError("Edges must be a list")

    graph = nx.Graph()

    for record in data["nodes"]:
        if not isinstance(record, dict):
            raise ValueError("Invalid node record")

        node = record.get("id")

        if not isinstance(node, str) or not node:
            raise ValueError("Invalid node ID")

        if node in graph:
            raise ValueError(f"Duplicate node: {node}")

        attributes = {}

        if "x" in record:
            attributes["x"] = record["x"]

        if "y" in record:
            attributes["y"] = record["y"]

        graph.add_node(node, **attributes)

    for record in data["edges"]:
        if not isinstance(record, dict):
            raise ValueError("Invalid edge record")

        u = record.get("source")
        v = record.get("target")

        if u not in graph or v not in graph:
            raise ValueError(
                f"Road references missing node: {u}-{v}"
            )

        if graph.has_edge(u, v):
            raise ValueError(f"Duplicate road: {u}-{v}")

        graph.add_edge(
            u, v, weight=record.get("weight")
        )

    validate_graph(graph)

    graph.graph["coordinate_system"] = data["coordinate_system"]
    graph.graph["source"] = data.get("source", "unknown")

    return graph


def save_graph(graph, filepath,
               coordinate_system="pixel",
               source="synthetic"):
    """Save the graph to JSON."""
    data = graph_to_dict(
        graph,
        coordinate_system=coordinate_system,
        source=source,
    )

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return filepath


def load_graph(filepath):
    """Load a graph from JSON."""
    with Path(filepath).open("r", encoding="utf-8") as file:
        data = json.load(file)

    return graph_from_dict(data)
