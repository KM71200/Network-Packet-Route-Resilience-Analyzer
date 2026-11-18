import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def draw_network(
    graph,
    original_route=None,
    failed_edge=None,
    alternative_route=None
):
    """
    Visualize the weighted directed network.

    Blue  -> Original optimal route
    Green -> Alternative route
    Red   -> Failed link
    Gray  -> Normal network links
    """

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Keep node positions consistent
    pos = nx.spring_layout(graph, seed=42)

    # Draw nodes
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=1800,
        ax=ax
    )

    # Draw node labels
    nx.draw_networkx_labels(
        graph,
        pos,
        font_size=12,
        font_weight="bold",
        ax=ax
    )

    # Draw normal network edges
    nx.draw_networkx_edges(
        graph,
        pos,
        edge_color="gray",
        width=2,
        arrows=True,
        arrowsize=20,
        ax=ax
    )

    # Display edge weights
    edge_labels = nx.get_edge_attributes(graph, "weight")

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=10,
        ax=ax
    )

    # Highlight original optimal route
    if original_route:
        original_edges = list(
            zip(original_route[:-1], original_route[1:])
        )

        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=original_edges,
            edge_color="blue",
            width=4,
            arrows=True,
            arrowsize=22,
            ax=ax
        )

    # Highlight alternative route
    if alternative_route:
        alternative_edges = list(
            zip(alternative_route[:-1], alternative_route[1:])
        )

        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=alternative_edges,
            edge_color="green",
            width=4,
            arrows=True,
            arrowsize=22,
            ax=ax
        )

    # Draw failed edge LAST so it remains clearly visible
    if failed_edge:
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=[failed_edge],
            edge_color="red",
            width=5,
            style="dashed",
            arrows=True,
            arrowsize=24,
            ax=ax
        )

    # Legend
    legend_elements = [
        Line2D(
            [0], [0],
            color="gray",
            lw=2,
            label="Normal Link"
        ),
        Line2D(
            [0], [0],
            color="blue",
            lw=4,
            label="Original Route"
        ),
        Line2D(
            [0], [0],
            color="green",
            lw=4,
            label="Alternative Route"
        ),
        Line2D(
            [0], [0],
            color="red",
            lw=4,
            linestyle="--",
            label="Failed Link"
        )
    ]

    ax.legend(
        handles=legend_elements,
        loc="best"
    )

    ax.set_title(
        "Network Packet Route Visualization",
        fontsize=14,
        fontweight="bold"
    )

    ax.axis("off")

    plt.tight_layout()

    return fig