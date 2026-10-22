# from .data_processing import build_package_nodes
# from .graph_analysis import build_dependency_graph, compute_metrics
# from .reasoning_engine import generate_insight_cards
# from .evaluation import export_results, generate_experimental_summary
# from .visualization import save_graph_image


# def run_idrf(requirements_path:str):
#     """
#     Master orchestrator for the complete IDRF bounded pilot.

#     EXECUTION FLOW:
#     dependency ETL -> recursive metadata crawl -> graph build -> metric compute
#     -> investigative scoring -> insight generation -> export artifacts.

#     WHY THIS FUNCTION EXISTS:
#     It guarantees the whole experiment is runnable through one stable entry point,
#     which is essential for reproducibility and later sample-result generation.
#     """
#     nodes=build_package_nodes(requirements_path)
#     G=build_dependency_graph(nodes,requirements_path)
#     metrics=compute_metrics(G)
#     cards=generate_insight_cards(metrics)
#     export_results(metrics,cards)
#     save_graph_image(G)
#     generate_experimental_summary(metrics,cards)
#     return metrics,cards


# """
# IDRF Master Pipeline
# --------------------
# This module orchestrates the full bounded execution of the Investigative
# Dependency Reasoning Framework.

# Grounding:
# - Integrates all proposal modules into one reproducible experiment.
# - Corresponds to GitHub milestone closure of ETL -> Graph -> Reasoning -> Output.
# """

# from .data_processing import build_package_nodes
# from .graph_analysis import build_dependency_graph, compute_metrics
# from .reasoning_engine import generate_insight_cards
# from .evaluation import export_results, generate_experimental_summary
# from .visualization import save_graph_image


# def run_idrf(requirements_path: str):
#     """
#     Execute the complete bounded IDRF experiment.

#     Returns:
#     metrics dataframe,
#     generated insight cards,
#     experimental summary dictionary
#     """
#     nodes = build_package_nodes(requirements_path)
#     G = build_dependency_graph(nodes, requirements_path)
#     metrics = compute_metrics(G)
#     cards = generate_insight_cards(metrics)

#     export_results(metrics, cards)
#     save_graph_image(G)
#     summary = generate_experimental_summary(metrics, cards)

#     return metrics, cards, summary



"""
IDRF Master Pipeline
--------------------
Full bounded experiment orchestration with experiment-specific artifact saving.

Grounding:
- integrates ETL -> graph -> reasoning -> export
- preserves reproducible isolated evidence for each selected ecosystem
- directly supports Proposal Section 5.4 controlled experimentation
"""

from .data_processing import build_package_nodes
from .graph_analysis import build_dependency_graph, compute_metrics
from .reasoning_engine import generate_insight_cards, investigative_priority
from .evaluation import export_results, generate_experimental_summary
from .visualization import save_graph_image


def run_idrf(requirements_path: str, experiment_name: str, progress_callback=None):
    """
    Execute one complete bounded IDRF experiment.

    Parameters:
    requirements_path : analyst supplied dependency manifest
    experiment_name   : unique experiment folder label
    """
    output_dir = f"outputs/{experiment_name}"

    def progress(stage, status):
        if progress_callback is not None:
            progress_callback(stage, status)

    progress(1, "start")
    nodes = build_package_nodes(requirements_path)
    progress(1, "done")

    progress(2, "start")
    G = build_dependency_graph(nodes, requirements_path)
    progress(2, "done")

    progress(3, "start")
    metrics = compute_metrics(G)
    progress(3, "done")

    progress(4, "start")
    cards = generate_insight_cards(metrics)
    progress(4, "done")

    progress(5, "start")
    export_results(metrics, cards, output_dir)
    progress(5, "done")

    progress(6, "start")
    node_priority_scores = {
        row.package: investigative_priority(row)
        for _, row in metrics.iterrows()
    }
    save_graph_image(G, output_dir, node_priority_scores)
    progress(6, "done")

    progress(7, "start")
    summary = generate_experimental_summary(metrics, cards, output_dir)
    progress(7, "done")

    return metrics, cards, summary