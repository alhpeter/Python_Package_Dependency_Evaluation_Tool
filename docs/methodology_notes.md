# IDRF Methodology Notes

This document summarizes the computational methodology actually implemented in
this repository.

## Implemented Pipeline

1. Parse direct dependencies from a local requirements manifest.
2. Recursively retrieve bounded transitive dependency information from PyPI.
3. Retrieve bounded repository vitality metadata from GitHub when homepage links exist.
4. Construct a directed dependency graph.
5. Compute graph metrics and metadata-linked package indicators.
6. Apply transparent weighted investigative priority scoring.
7. Execute deterministic reasoning rules.
8. Generate human-readable investigative insight cards.
9. Export reproducibility artifacts.

## Important Methodological Constraint

Transitive recursion depth is intentionally capped at 2 to preserve reproducible
pilot-scale execution.

This should be reported in the paper as a bounded exploratory dependency closure,
not as exhaustive ecosystem mining.

## Metadata Sources Used

- PyPI JSON API
- GitHub Repository REST API (public endpoints only)

No proprietary or hidden package intelligence is used.