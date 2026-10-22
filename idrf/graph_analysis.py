# import networkx as nx
# import pandas as pd
# from dataclasses import asdict
# from typing import Dict
# from .models import PackageNode
# from .data_processing import extract_dependencies


# def build_dependency_graph(nodes:Dict[str,PackageNode],requirements_path:str)->nx.DiGraph:
#     """
#     Construct the directed dependency graph used by IDRF.

#     GRAPH SEMANTICS:
#     ROOT_PROJECT -> direct dependency
#     package -> child transitive dependency

#     WHY THIS FUNCTION EXISTS:
#     This fulfills GitHub issue #16 and proposal objective 'graph-based modeling'.
#     All later structural analytics depend on this graph object.
#     """
#     G=nx.DiGraph()
#     G.add_node('ROOT_PROJECT')
#     for dep in extract_dependencies(requirements_path):
#         G.add_edge('ROOT_PROJECT',dep)
#     for node in nodes.values():
#         G.add_node(node.name,**asdict(node))
#         for child in node.dependencies:
#             G.add_edge(node.name,child)
#     return G

# def compute_metrics(G:nx.DiGraph)->pd.DataFrame:
#     """
#     Compute baseline structural and metadata-linked metrics.

#     METRICS INCLUDED:
#     - betweenness centrality: structural brokerage/influence
#     - indegree: number of upstream dependents
#     - outdegree: propagation breadth to child dependencies
#     - depth: transitive distance from root project
#     - stars/open_issues/last_update_days/maintainer_count: metadata vitality

#     WHY THIS FUNCTION EXISTS:
#     This directly implements GitHub issue #17 and proposal objective on
#     structural characteristic analysis.
#     """
#     centrality=nx.betweenness_centrality(G)
#     indegree=dict(G.in_degree())
#     outdegree=dict(G.out_degree())
#     rows=[]
#     for n in G.nodes:
#         if n=='ROOT_PROJECT':
#             continue
#         attrs=G.nodes[n]
#         try:
#             depth=nx.shortest_path_length(G,'ROOT_PROJECT',n)
#         except:
#             depth=0
#         rows.append({
#             'package':n,
#             'centrality':round(centrality.get(n,0),4),
#             'indegree':indegree.get(n,0),
#             'outdegree':outdegree.get(n,0),
#             'depth':depth,
#             'stars':attrs.get('stars',10),
#             'open_issues':attrs.get('open_issues',0),
#             'last_update_days':attrs.get('last_update_days',365),
#             'maintainer_count':attrs.get('maintainer_count',1)
#         })
#     return pd.DataFrame(rows)
"""
IDRF Graph Analysis Module
--------------------------

WHY THIS MODULE EXISTS
----------------------
This module converts bounded package metadata into a directed dependency graph
and computes the structural indicators required by the investigative reasoning layer.

GROUNDING TO PROJECT
--------------------
Implements:

- Proposal Section 5.2 Dependency Modeling and Structural Analysis
- GitHub Issues #16 and #17

GRAPH INTERPRETATION
--------------------
ROOT_PROJECT -> analyst listed dependency
dependency -> bounded immediate contextual dependency

This graph is intentionally bounded rather than internet-complete.
The goal is analytical reasoning support, not ecosystem crawling.
"""

import networkx as nx
import pandas as pd
from dataclasses import asdict
from typing import Dict
from .models import PackageNode
from .data_processing import extract_dependencies


def build_dependency_graph(nodes: Dict[str, PackageNode], requirements_path: str) -> nx.DiGraph:
    """
    Construct the bounded directed dependency graph.

    WHY THIS FUNCTION EXISTS
    ------------------------
    All later centrality, depth, propagation, and reasoning operations depend
    on a coherent graph object.

    V4 GRAPH POLICY
    ---------------
    Root project points to analyst-specified packages.
    Each retained package points only to its bounded immediate children.
    """
    G = nx.DiGraph()
    G.add_node("ROOT_PROJECT")

    root_dependencies = extract_dependencies(requirements_path)

    for dep in root_dependencies:
        G.add_edge("ROOT_PROJECT", dep)

    for node in nodes.values():
        G.add_node(node.name, **asdict(node))

        for child in node.direct_dependencies:
            G.add_edge(node.name, child)

    return G


def compute_metrics(G: nx.DiGraph) -> pd.DataFrame:
    """
    Compute graph and metadata metrics used by IDRF reasoning.

    INCLUDED METRICS
    ----------------
    centrality:
        Betweenness centrality proxy for structural brokerage importance.

    indegree:
        Number of incoming upstream dependency links.

    outdegree:
        Number of outgoing bounded child dependencies.

    depth:
        Distance from analyst root project.

    stars:
        Public ecosystem visibility proxy.

    last_update_days:
        Repository maintenance freshness proxy.

    maintainer_count:
        Maintainer concentration proxy.

    WHY THESE METRICS
    -----------------
    These are the exact bounded interpretable variables used by the proposal's
    reasoning-oriented analytical layer.
    """
    centrality = nx.betweenness_centrality(G)
    indegree = dict(G.in_degree())
    outdegree = dict(G.out_degree())

    rows = []

    for n in G.nodes:
        if n == "ROOT_PROJECT":
            continue

        attrs = G.nodes[n]

        try:
            depth = nx.shortest_path_length(G, "ROOT_PROJECT", n)
        except:
            depth = 0

        rows.append({
            "package": n,
            "centrality": round(centrality.get(n, 0), 4),
            "indegree": indegree.get(n, 0),
            "outdegree": outdegree.get(n, 0),
            "depth": depth,
            "stars": attrs.get("stars", 10),
            "last_update_days": attrs.get("last_update_days", 365),
            "maintainer_count": attrs.get("maintainer_count", 1)
        })

    return pd.DataFrame(rows)