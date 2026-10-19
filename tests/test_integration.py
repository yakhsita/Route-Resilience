
import json

from src.graph.routing import create_graph
from src.graph.criticality import create_vulnerable_graph
from src.graph.graph_io import save_graph, load_graph
from src.graph.integration import analyze_network


def test_imported_graph_routing(tmp_path):
    filepath = tmp_path / "graph.json"
    save_graph(create_graph(), filepath)

    graph = load_graph(filepath)
    report = analyze_network(graph, "A", "I")

    assert report["routing"]["distance"] == 9
    assert report["routing"]["path"] == [
        "A", "D", "E", "H", "I"
    ]


def test_imported_graph_closure(tmp_path):
    filepath = tmp_path / "graph.json"
    save_graph(create_graph(), filepath)

    graph = load_graph(filepath)
    report = analyze_network(
        graph, "A", "I", closed_roads=[("D", "E")]
    )

    failure = report["failure_scenario"]

    assert failure["new_distance"] == 12
    assert failure["lost_pairs"] == 0


def test_imported_vulnerable_graph(tmp_path):
    filepath = tmp_path / "vulnerable.json"
    save_graph(create_vulnerable_graph(), filepath)

    graph = load_graph(filepath)
    report = analyze_network(
        graph, "A", "F", closed_roads=[("C", "D")]
    )

    assert ["C", "D"] in report["criticality"]["bridges"]
    assert set(
        report["criticality"]["articulation_points"]
    ) == {"C", "D"}

    assert report["failure_scenario"]["lost_pairs"] == 9


def test_vulnerability_covers_every_road():
    graph = create_graph()
    report = analyze_network(graph, "A", "I")

    assert len(report["vulnerability"]) == 14


def test_integrated_report_json_serializable():
    graph = create_graph()
    report = analyze_network(graph, "A", "I")

    encoded = json.dumps(report)
    assert isinstance(encoded, str)


def test_integration_does_not_modify_graph():
    graph = create_graph()
    original_edges = set(graph.edges())

    analyze_network(
        graph,
        "A",
        "I",
        closed_roads=[("D", "E")],
    )

    assert set(graph.edges()) == original_edges
