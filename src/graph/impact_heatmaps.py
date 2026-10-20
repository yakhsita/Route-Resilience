
"""
Day 13: Two measured-impact heatmaps.

Map 1: Sampled connectivity loss (%).
Map 2: Total additional distance (metres).

Gray = not evaluated.
Green = zero measured impact.
Yellow/red = increasing measured impact.

All road closures are hypothetical.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import osmnx as ox

from src.graph.criticality_heatmap import (
    load_criticality_report,
    edge_coordinates,
)


GRAPH_PATH = Path(
    "G:/Route-Resilience/data/raw/koramangala_roads.graphml"
)

OUTPUT_PATH = Path(
    "data/processed/koramangala_impact_heatmaps.png"
)


def prepare_metric_data(graph, results, metric):
    """
    Prepare actual measured values for each directed edge.

    No rank-based color assignment.
    Equal values receive equal colors.
    """
    allowed_metrics = {
        "connectivity_loss_percent",
        "total_extra_metres",
    }

    if metric not in allowed_metrics:
        raise ValueError(
            f"Unsupported impact metric: {metric}"
        )

    segments = []
    values = []
    edge_ids = []

    for item in results:
        u, v, key = item["edge"]

        if not graph.has_edge(u, v, key):
            raise ValueError(
                f"Missing road edge: {(u, v, key)}"
            )

        value = float(item[metric])

        if not 0 <= value < float("inf"):
            raise ValueError(
                f"Invalid impact value: {value}"
            )

        segments.append(
            edge_coordinates(graph, u, v, key)
        )

        values.append(value)
        edge_ids.append((u, v, key))

    return segments, values, edge_ids


def draw_metric_map(
    graph,
    results,
    metric,
    ax,
    fig,
    title,
    colorbar_label,
):
    """
    Draw one impact map on an existing Matplotlib axis.
    """
    segments, values, edge_ids = prepare_metric_data(
        graph, results, metric
    )

    ox.plot_graph(
        graph,
        ax=ax,
        node_size=0,
        edge_color="#C8C8C8",
        edge_linewidth=0.55,
        bgcolor="white",
        show=False,
        close=False,
    )

    if segments:
        maximum = max(values)

        # Keep zero at the bottom of the scale.
        # Avoid a zero-width color range.
        upper_bound = maximum if maximum > 0 else 1.0

        norm = Normalize(
            vmin=0,
            vmax=upper_bound,
        )

        collection = LineCollection(
            segments,
            cmap="RdYlGn_r",
            norm=norm,
            linewidths=4,
            zorder=10,
        )

        collection.set_array(values)
        ax.add_collection(collection)

        colorbar = fig.colorbar(
            ScalarMappable(
                norm=norm,
                cmap="RdYlGn_r",
            ),
            ax=ax,
            fraction=0.035,
            pad=0.02,
        )

        colorbar.set_label(colorbar_label)

        if maximum == 0:
            colorbar.set_ticks([0])
            colorbar.set_ticklabels(["0"])

    ax.set_title(title, fontsize=12)

    return {
        "evaluated_edges": len(edge_ids),
        "maximum_impact": max(values, default=0.0),
    }


def draw_impact_heatmaps(
    graph,
    results,
    output_path=OUTPUT_PATH,
    show=True,
):
    """
    Generate two side-by-side maps using actual
    measured impact values.
    """
    fig, axes = plt.subplots(
        1, 2,
        figsize=(18, 9),
    )

    fig.patch.set_facecolor("white")

    connectivity_info = draw_metric_map(
        graph,
        results,
        metric="connectivity_loss_percent",
        ax=axes[0],
        fig=fig,
        title="A. Connectivity Loss",
        colorbar_label="Sampled journeys disconnected (%)",
    )

    detour_info = draw_metric_map(
        graph,
        results,
        metric="total_extra_metres",
        ax=axes[1],
        fig=fig,
        title="B. Additional Travel Distance",
        colorbar_label="Total additional distance (m)",
    )

    fig.suptitle(
        "Route Resilience - Koramangala\n"
        "Simulated Directed Road Closure Impact",
        fontsize=16,
    )

    fig.text(
        0.5,
        0.025,
        "Gray: not evaluated | Colored: evaluated "
        "road edges | Sample-based analysis, not live incidents",
        ha="center",
        fontsize=10,
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
        facecolor="white",
    )

    print("\n===== IMPACT HEATMAP SUMMARY =====")
    print(
        "Evaluated edges:",
        connectivity_info["evaluated_edges"],
    )
    print(
        "Maximum connectivity loss:",
        connectivity_info["maximum_impact"],
        "%",
    )
    print(
        "Maximum total extra distance:",
        detour_info["maximum_impact"],
        "metres",
    )
    print("Heatmaps saved to:", output_path)

    if show:
        plt.show()
    else:
        plt.close(fig)

    return output_path


def main():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"OSM graph not found: {GRAPH_PATH}"
        )

    graph = ox.load_graphml(GRAPH_PATH)
    results = load_criticality_report()

    draw_impact_heatmaps(graph, results)


if __name__ == "__main__":
    main()
