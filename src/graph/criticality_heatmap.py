
"""
Day 12: Criticality heatmap for Koramangala.

Visualizes simulated directed-edge closure impact.

Red: highest measured impact
Orange/yellow: intermediate impact
Green: lower measured impact
Gray: not evaluated

This is NOT a flood-risk or live-closure map.
"""

from pathlib import Path
import json

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import osmnx as ox


GRAPH_PATH = Path(
    "G:/Route-Resilience/data/raw/koramangala_roads.graphml"
)

REPORT_PATH = Path(
    "data/processed/koramangala_criticality.json"
)

OUTPUT_PATH = Path(
    "data/processed/koramangala_criticality_heatmap.png"
)


def load_criticality_report(path=REPORT_PATH):
    """Read the Day 11 JSON report."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Criticality report not found: {path}\n"
            "Run: python -m src.graph.real_criticality"
        )

    with path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    if report.get("analysis") != (
        "sampled_directed_edge_criticality"
    ):
        raise ValueError(
            "Unexpected criticality report format."
        )

    return report["results"]


def edge_coordinates(graph, u, v, key):
    """Return the map coordinates of one OSM edge."""
    data = graph[u][v][key]

    if "geometry" in data:
        return list(data["geometry"].coords)

    return [
        (
            graph.nodes[u]["x"],
            graph.nodes[u]["y"],
        ),
        (
            graph.nodes[v]["x"],
            graph.nodes[v]["y"],
        ),
    ]


def prepare_heatmap_data(graph, results):
    """
    Convert ranked criticality results into segments
    and normalized visualization scores.

    Visualization ordering:
      1. Lost journeys
      2. Total extra metres

    Scores are display ranks, not physical risk
    probabilities or calibrated vulnerability scores.
    """
    if not results:
        return [], [], []

    ordered = sorted(
        results,
        key=lambda item: (
            item["lost_journeys"],
            item["total_extra_metres"],
        ),
    )

    segments = []
    scores = []
    edge_ids = []

    count = len(ordered)

    for index, item in enumerate(ordered):
        u, v, key = item["edge"]

        if not graph.has_edge(u, v, key):
            raise ValueError(
                f"Criticality edge missing: {(u, v, key)}"
            )

        segments.append(
            edge_coordinates(graph, u, v, key)
        )

        # Relative display rank from 0 to 1.
        score = (
            index / (count - 1)
            if count > 1 else 1.0
        )

        scores.append(score)
        edge_ids.append((u, v, key))

    return segments, scores, edge_ids


def draw_heatmap(
    graph,
    results,
    output_path=OUTPUT_PATH,
    show=True,
):
    """
    Draw the road network and highlight evaluated edges.
    """
    segments, scores, edge_ids = prepare_heatmap_data(
        graph, results
    )

    fig, ax = ox.plot_graph(
        graph,
        node_size=0,
        edge_color="#B8B8B8",
        edge_linewidth=0.55,
        bgcolor="white",
        show=False,
        close=False,
        figsize=(12, 10),
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    if segments:
        collection = LineCollection(
            segments,
            cmap="RdYlGn_r",
            norm=Normalize(vmin=0, vmax=1),
            linewidths=4,
            zorder=10,
        )

        collection.set_array(scores)
        ax.add_collection(collection)

        colorbar = fig.colorbar(
            ScalarMappable(
                norm=Normalize(vmin=0, vmax=1),
                cmap="RdYlGn_r",
            ),
            ax=ax,
            fraction=0.035,
            pad=0.02,
        )

        colorbar.set_label(
            "Relative rank among evaluated edges"
        )

    ax.set_title(
        "Route Resilience - Koramangala Road Criticality\n"
        "Sampled directional closure impact",
        fontsize=14,
    )

    from matplotlib.lines import Line2D

    legend_items = [
        Line2D(
            [0], [0],
            color="#B8B8B8",
            linewidth=2,
            label="Not evaluated",
        ),
        Line2D(
            [0], [0],
            color="#22C55E",
            linewidth=4,
            label="Lower relative impact",
        ),
        Line2D(
            [0], [0],
            color="#DC2626",
            linewidth=4,
            label="Higher relative impact",
        ),
    ]

    ax.legend(
        handles=legend_items,
        loc="upper right",
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    print("Heatmap saved to:", output_path)
    print("Evaluated directed edges:", len(edge_ids))

    if show:
        plt.show()
    else:
        plt.close(fig)

    return output_path


def main():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(GRAPH_PATH)

    graph = ox.load_graphml(GRAPH_PATH)
    results = load_criticality_report()

    draw_heatmap(graph, results)


if __name__ == "__main__":
    main()
