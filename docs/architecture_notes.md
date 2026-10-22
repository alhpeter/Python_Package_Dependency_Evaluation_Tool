# IDRF Architecture Notes

The implemented architecture follows the high-level architecture proposed in the
IDRF concept note.

## Layer 1 — Data Processing Layer
Requirements parsing + PyPI/GitHub metadata retrieval.

## Layer 2 — Dependency Graph Modeling Layer
Directed graph construction using package-to-package dependency relations.

## Layer 3 — Structural Analytics Layer
Computation of centrality, indegree, outdegree, and root-depth.

## Layer 4 — Investigative Reasoning Layer
Weighted prioritization and explicit reasoning rule triggers.

## Layer 5 — Insight Generation Layer
Transformation of numerical anomalies into human-readable investigative cards.

## Layer 6 — Evaluation and Artifact Layer
CSV, JSON, and PNG output generation for reproducible reporting.