"""
WHY THE CONSTANTS BELOW EXIST
-----------------------------
HIGH_CENTRALITY_THRESHOLD = 0.08
    In bounded pilot graphs, centrality values are naturally sparse.
    A lower but explicit threshold is needed so structurally important nodes are
    not ignored during small-sample experimentation.

STALE_UPDATE_DAYS = 180
    Six months without repository push activity is used as a conservative
    maintenance staleness signal.

LOW_MAINTAINER_THRESHOLD = 1
    Because maintainer_count here is a metadata proxy, only the strongest case
    of single-maintainer concentration is flagged.

LOW_STAR_THRESHOLD = 50
    Very low public visibility is treated as a weak ecosystem support signal.

MAX_TRANSITIVE_DEPTH = 2
    Full unconstrained recursion would create unstable conference-time runs.
    A depth of two preserves meaningful transitive structure while keeping the
    pilot bounded and reproducible.

REQUEST_TIMEOUT = 8
    Prevents network hangs from crashing the experiment.

WEIGHT_* constants
    These weights form a transparent additive Investigative Priority Score.
    They are intentionally balanced rather than learned so every output remains
    interpretable during paper defense.
"""

# HIGH_CENTRALITY_THRESHOLD = 0.08
# STALE_UPDATE_DAYS = 180
# LOW_MAINTAINER_THRESHOLD = 1
# LOW_STAR_THRESHOLD = 50
# MAX_TRANSITIVE_DEPTH = 2
# REQUEST_TIMEOUT = 8

# # WEIGHT_CENTRALITY = 0.25
# # WEIGHT_DEPTH = 0.20
# # WEIGHT_STALENESS = 0.20
# # WEIGHT_MAINTAINER = 0.20
# # WEIGHT_POPULARITY = 0.15
# WEIGHT_CENTRALITY = 0.22
# WEIGHT_DEPTH = 0.18
# WEIGHT_STALENESS = 0.20
# WEIGHT_MAINTAINER = 0.18
# WEIGHT_POPULARITY = 0.12
# WEIGHT_CONNECTIVITY = 0.10
# HIGH_CENTRALITY_THRESHOLD = 0.025
# STALE_UPDATE_DAYS = 120
# LOW_MAINTAINER_THRESHOLD = 1
# LOW_STAR_THRESHOLD = 40
# MAX_TRANSITIVE_DEPTH = 2
# REQUEST_TIMEOUT = 8

# WEIGHT_CENTRALITY = 0.28
# WEIGHT_DEPTH = 0.15
# WEIGHT_STALENESS = 0.18
# WEIGHT_MAINTAINER = 0.15
# WEIGHT_POPULARITY = 0.09
# WEIGHT_CONNECTIVITY = 0.15

HIGH_CENTRALITY_THRESHOLD = 0.08
STALE_UPDATE_DAYS = 300
LOW_MAINTAINER_THRESHOLD = 1
LOW_STAR_THRESHOLD = 50
MAX_TRANSITIVE_DEPTH = 2
REQUEST_TIMEOUT = 8

WEIGHT_CENTRALITY = 0.24
WEIGHT_DEPTH = 0.16
WEIGHT_STALENESS = 0.18
WEIGHT_MAINTAINER = 0.16
WEIGHT_POPULARITY = 0.10
WEIGHT_CONNECTIVITY = 0.16

GITHUB_API = "https://api.github.com/repos/"