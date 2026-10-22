# import os
# import matplotlib.pyplot as plt
# import networkx as nx


# def save_graph_image(G:nx.DiGraph):
#     """Save a visual dependency network figure."""
#     os.makedirs('outputs',exist_ok=True)
#     plt.figure(figsize=(12,8))
#     pos=nx.spring_layout(G,seed=42)
#     nx.draw(G,pos,with_labels=True,node_size=700,font_size=7)
#     plt.tight_layout()
#     plt.savefig('outputs/dependency_graph.png')
#     plt.close()


# import os
# import matplotlib.pyplot as plt
# import networkx as nx


# def save_graph_image(G: nx.DiGraph):
#     os.makedirs("outputs", exist_ok=True)

#     plt.figure(figsize=(12, 8))
#     pos = nx.spring_layout(G, seed=42, k=1.2)

#     nx.draw(
#         G,
#         pos,
#         with_labels=True,
#         node_size=900,
#         font_size=8
#     )

#     plt.savefig("outputs/dependency_graph.png", bbox_inches="tight")
#     plt.close()


import os
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D


def save_graph_image(G: nx.DiGraph, output_dir: str, node_priority_scores: dict[str, float]):
    """
    Save experiment-specific dependency graph artifact.

    WHY:
    Visual graph evidence is required for conference and major-project reporting.
    """
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(20, 16))

    depths = {}

    for node in G.nodes:
        try:
            depths[node] = nx.shortest_path_length(
                G,
                "ROOT_PROJECT",
                node
            )
        except Exception:
            depths[node] = 0

    levels = {}

    for node, depth in depths.items():
        levels.setdefault(depth, []).append(node)

    pos = {}

    for depth, nodes in levels.items():
        width = len(nodes)

        for i, node in enumerate(nodes):

            # More horizontal spacing
            x = (i - width / 2) * 2.5

            # More vertical spacing
            y = -depth * 1.5

            pos[node] = (x, y)

    depth_colors = {
        1: "#56CCF2",
        2: "#c68ee6",
    }
    node_colors = []
    node_sizes = []

    for node in G.nodes:
        if node == "ROOT_PROJECT":
            node_colors.append("#F2C94C")
            node_sizes.append(1600)
        else:
            node_colors.append(depth_colors.get(depths[node], "#6FCF97"))
            score = max(0, min(node_priority_scores.get(node, 0), 1))
            node_sizes.append(350 + score * 2200)

    # Shorten very long labels
    labels = {}

    for node in G.nodes:
        if node == "ROOT_PROJECT":
            labels[node] = "ROOT_PROJECT"
        elif len(node) > 18:
            labels[node] = node[:15] + "..."
        else:
            labels[node] = node

    nx.draw(
        G,
        pos,
        labels=labels,
        node_color=node_colors,
        node_size=node_sizes,
        font_size=6,
        font_color="black",
        edge_color="#666666",
        linewidths=1,
        arrows=True,
        arrowsize=12
    )

    plt.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="", color="#F2C94C", label="Project root"),
            Line2D([], [], marker="o", linestyle="", color=depth_colors[1], label="Direct dependency"),
            Line2D([], [], marker="o", linestyle="", color=depth_colors[2], label="2 levels deep"),
            Line2D([], [], marker="o", linestyle="", color="#888888", markersize=6, label="Lower score"),
            Line2D([], [], marker="o", linestyle="", color="#888888", markersize=13, label="Higher score"),
        ],
        title="Color = dependency depth; size = investigation score",
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
        frameon=False,
    )
    plt.axis("off")

    plt.savefig(
        os.path.join(output_dir, "dependency_graph.png"),
        bbox_inches="tight",
        dpi=300
    )

    plt.close()