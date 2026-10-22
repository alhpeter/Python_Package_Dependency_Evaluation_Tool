# from typing import List
# from .models import InsightCard
# from .config import *
# import pandas as pd


# def investigative_priority(row)->float:
#     """
#     Compute the transparent Investigative Priority Score.

#     WHY THIS FUNCTION EXISTS:
#     Raw metrics alone create cognitive overload. The proposal specifically seeks
#     a reasoning-oriented prioritization mechanism.

#     WHY ADDITIVE WEIGHTING IS USED:
#     A deterministic weighted sum is fully interpretable. Reviewers can trace why
#     one dependency outranks another, unlike black-box predictive models.
#     """
#     c=min(row.centrality,1)
#     d=min(row.depth/MAX_TRANSITIVE_DEPTH,1)
#     s=min(row.last_update_days/365,1)
#     m=1 if row.maintainer_count<=LOW_MAINTAINER_THRESHOLD else 0
#     p=1 if row.stars<=LOW_STAR_THRESHOLD else 0
#     k=min(row.outdegree/5,1)
#     return round(WEIGHT_CENTRALITY*c+WEIGHT_DEPTH*d+WEIGHT_STALENESS*s+WEIGHT_MAINTAINER*m+WEIGHT_POPULARITY*p+WEIGHT_CONNECTIVITY*k,3)

# def generate_insight_cards(metrics_df:pd.DataFrame)->List[InsightCard]:
#     """
#     Convert numerical observations into structured investigative findings.

#     WHY THIS FUNCTION EXISTS:
#     This is the core novelty layer corresponding to GitHub issues #18, #19, #20,
#     and #21. Instead of printing raw anomalies, the framework generates explicit
#     human-facing reasoning statements and follow-up investigative prompts.
#     """
#     cards=[]
#     for _,row in metrics_df.iterrows():
#         triggers=[]
#         if row.centrality>=HIGH_CENTRALITY_THRESHOLD: triggers.append('high structural influence')
#         if row.last_update_days>=STALE_UPDATE_DAYS: triggers.append('maintenance staleness')
#         if row.maintainer_count<=LOW_MAINTAINER_THRESHOLD: triggers.append('maintainer concentration proxy')
#         if row.stars<=LOW_STAR_THRESHOLD: triggers.append('low ecosystem visibility')
#         if row.depth>=2: triggers.append('deep transitive placement')
#         if row.outdegree>=2: triggers.append('dependency propagation breadth')
#         if triggers:
#             cards.append(InsightCard(
#                 package=row.package,
#                 investigative_priority_score=investigative_priority(row),
#                 finding='Dependency exhibits '+', '.join(triggers)+'.',
#                 rationale=f'Combined graph topology and public metadata suggest elevated investigative priority for {row.package}.',
#                 recommended_question='Does this package warrant substitution, architectural buffering, or explicit monitoring?'
#             ))
#     cards.sort(key=lambda x:x.investigative_priority_score,reverse=True)
#     return cards


# from typing import List
# from .models import InsightCard
# from .config import *
# import pandas as pd


# def investigative_priority(row) -> float:
#     """
#     Transparent weighted Investigative Priority Score.

#     WHY:
#     Implements GitHub issues #19 #20 #21:
#     structured interpretable reasoning rather than black-box prediction.
#     """
#     c = min(row.centrality, 1)
#     d = min(row.depth / MAX_TRANSITIVE_DEPTH, 1)
#     s = min(row.last_update_days / 365, 1)
#     m = 1 if row.maintainer_count <= LOW_MAINTAINER_THRESHOLD else 0
#     p = 1 if row.stars <= LOW_STAR_THRESHOLD else 0
#     k = min(row.outdegree / 3, 1)

#     return round(
#         WEIGHT_CENTRALITY * c +
#         WEIGHT_DEPTH * d +
#         WEIGHT_STALENESS * s +
#         WEIGHT_MAINTAINER * m +
#         WEIGHT_POPULARITY * p +
#         WEIGHT_CONNECTIVITY * k,
#         3
#     )


# def generate_insight_cards(metrics_df: pd.DataFrame) -> List[InsightCard]:
#     """
#     Generate selective analyst-facing reasoning cards.

#     V4 CHANGE:
#     ----------
#     Previous versions generated a card for almost every package.

#     IDRF should prioritize, not enumerate.

#     Therefore a package must satisfy MULTIPLE investigative triggers
#     before surfacing as an analyst attention candidate.
#     """
#     cards = []

#     for _, row in metrics_df.iterrows():
#         triggers = []

#         if row.centrality >= HIGH_CENTRALITY_THRESHOLD:
#             triggers.append("high structural influence")

#         if row.last_update_days >= STALE_UPDATE_DAYS:
#             triggers.append("maintenance staleness")

#         if row.maintainer_count <= LOW_MAINTAINER_THRESHOLD:
#             triggers.append("maintainer concentration proxy")

#         if row.stars <= LOW_STAR_THRESHOLD:
#             triggers.append("low ecosystem visibility")

#         if row.depth >= 1:
#             triggers.append("transitive placement")

#         if row.outdegree >= 2:
#             triggers.append("dependency propagation breadth")

#         # IMPORTANT V4 SELECTIVITY RULE:
#         if len(triggers) >= 2:
#             cards.append(
#                 InsightCard(
#                     package=row.package,
#                     investigative_priority_score=investigative_priority(row),
#                     finding="Dependency exhibits " + ", ".join(triggers) + ".",
#                     rationale=f"Combined structural and metadata indicators suggest elevated investigative attention for {row.package}.",
#                     recommended_question="Should this dependency be buffered, substituted, or explicitly monitored?"
#                 )
#             )

#     cards.sort(key=lambda x: x.investigative_priority_score, reverse=True)
#     return cards[:10]











from typing import Any, Dict, List
from .models import InsightCard
from .config import *
import pandas as pd

def investigative_priority(row) -> float:
    """
    Transparent weighted Investigative Priority Score.

    WHY:
    Implements GitHub issues #19 #20 #21:
    structured interpretable reasoning rather than black-box prediction.
    """
    c = min(row.centrality, 1)
    d = min(row.depth / MAX_TRANSITIVE_DEPTH, 1)
    s = min(row.last_update_days / 365, 1)
    m = 1 if row.maintainer_count <= LOW_MAINTAINER_THRESHOLD else 0
    p = 1 if row.stars <= LOW_STAR_THRESHOLD else 0
    k = min(row.outdegree / 3, 1)

    return round(
        WEIGHT_CENTRALITY * c +
        WEIGHT_DEPTH * d +
        WEIGHT_STALENESS * s +
        WEIGHT_MAINTAINER * m +
        WEIGHT_POPULARITY * p +
        WEIGHT_CONNECTIVITY * k,
        3
    )


def score_components(row) -> Dict[str, float]:
    """Return the existing weighted score inputs for transparent display."""
    return {
        "structural_influence": round(WEIGHT_CENTRALITY * min(row.centrality, 1), 3),
        "dependency_propagation": round(WEIGHT_DEPTH * min(row.depth / MAX_TRANSITIVE_DEPTH, 1), 3),
        "maintenance_signal": round(WEIGHT_STALENESS * min(row.last_update_days / 365, 1), 3),
        "maintainer_concentration": round(
            WEIGHT_MAINTAINER * (1 if row.maintainer_count <= LOW_MAINTAINER_THRESHOLD else 0), 3
        ),
        "ecosystem_visibility": round(
            WEIGHT_POPULARITY * (1 if row.stars <= LOW_STAR_THRESHOLD else 0), 3
        ),
        "connectivity": round(WEIGHT_CONNECTIVITY * min(row.outdegree / 3, 1), 3),
    }


def evidence_for_row(row) -> Dict[str, Any]:
    """Build a JSON-safe evidence bundle from metrics already computed by IDRF."""
    return {
        "centrality": float(row.centrality),
        "depth": int(row.depth),
        "indegree": int(row.indegree),
        "outdegree": int(row.outdegree),
        "stars": int(row.stars),
        "last_update_days": int(row.last_update_days),
        "maintainer_count": int(row.maintainer_count),
        "score_components": score_components(row),
    }


def rules_and_profiles(row) -> tuple[List[str], List[str], List[str]]:
    """Map existing rule conditions to stable identifiers and investigation categories."""
    rules = []
    profiles = []
    trigger_text = []

    if row.centrality >= HIGH_CENTRALITY_THRESHOLD:
        rules.append("HIGH_CENTRALITY")
        profiles.append("Structural Exposure")
        trigger_text.append("high structural influence")
    if row.depth >= 2:
        rules.append("TRANSITIVE_DEPENDENCY")
        profiles.append("Propagation Exposure")
        trigger_text.append("transitive placement")
    if row.outdegree >= 2:
        rules.append("PROPAGATION_BREADTH")
        profiles.append("Dependency Connectivity")
        trigger_text.append("dependency propagation breadth")
    if row.indegree >= 2:
        rules.append("SHARED_UPSTREAM_CONVERGENCE")
        profiles.append("Structural Exposure")
        trigger_text.append("shared upstream convergence")
    if row.last_update_days >= STALE_UPDATE_DAYS:
        rules.append("STALE_MAINTENANCE")
        profiles.append("Maintenance Signal")
        trigger_text.append("maintenance staleness")
    if row.maintainer_count <= LOW_MAINTAINER_THRESHOLD:
        rules.append("MAINTAINER_CONCENTRATION")
        profiles.append("Maintainer Concentration")
        trigger_text.append("maintainer concentration proxy")
    if row.stars <= LOW_STAR_THRESHOLD:
        rules.append("LOW_ECOSYSTEM_VISIBILITY")
        profiles.append("Ecosystem Visibility")
        trigger_text.append("low ecosystem visibility")

    return rules, list(dict.fromkeys(profiles)), trigger_text

# def generate_insight_cards(metrics_df: pd.DataFrame) -> List[InsightCard]:
#     """
#     Generate selective analyst-facing reasoning cards.

#     V5:
#     IDRF must reduce analyst overload, not flag every package.
#     """
#     cards = []

#     for _, row in metrics_df.iterrows():
#         triggers = []

#         if row.centrality >= HIGH_CENTRALITY_THRESHOLD:
#             triggers.append("high structural influence")

#         if row.last_update_days >= STALE_UPDATE_DAYS:
#             triggers.append("maintenance staleness")

#         if row.maintainer_count <= LOW_MAINTAINER_THRESHOLD:
#             triggers.append("maintainer concentration proxy")

#         if row.stars <= LOW_STAR_THRESHOLD:
#             triggers.append("low ecosystem visibility")

#         if row.depth >= 2:
#             triggers.append("transitive placement")

#         if row.outdegree >= 2:
#             triggers.append("dependency propagation breadth")

#         score = investigative_priority(row)

#         # if len(triggers) >= 2 and score >= 0.45:
#         #     cards.append(
#         #         InsightCard(
#         #             package=row.package,
#         #             investigative_priority_score=score,
#         #             finding="Dependency exhibits " + ", ".join(triggers) + ".",
#         #             rationale=f"Combined structural and metadata indicators suggest elevated investigative attention for {row.package}.",
#         #             recommended_question="Should this dependency be buffered, substituted, or explicitly monitored?"
#         #         )
#         #     )
#         score = investigative_priority(row)

#         structural_signal = (
#             row.centrality >= HIGH_CENTRALITY_THRESHOLD or
#             row.outdegree >= 1 or
#             row.depth >= 2
#         )

#         metadata_signal_count = 0
#         if row.last_update_days >= STALE_UPDATE_DAYS:
#             metadata_signal_count += 1
#         if row.maintainer_count <= LOW_MAINTAINER_THRESHOLD:
#             metadata_signal_count += 1
#         if row.stars <= LOW_STAR_THRESHOLD:
#             metadata_signal_count += 1

#         if structural_signal and (metadata_signal_count >= 1 or len(triggers) >= 2):
#             cards.append(
#                 InsightCard(
#                     package=row.package,
#                     investigative_priority_score=score,
#                     finding="Dependency exhibits " + ", ".join(triggers) + ".",
#                     rationale=f"Combined structural and metadata indicators suggest elevated investigative attention for {row.package}.",
#                     recommended_question="Should this dependency be buffered, substituted, or explicitly monitored?"
#                 )
#             )        

#     cards.sort(key=lambda x: x.investigative_priority_score, reverse=True)
#     return cards[:5]

def generate_insight_cards(metrics_df: pd.DataFrame) -> List[InsightCard]:
    """
    Generate bounded analyst-facing investigative reasoning cards.

    CONFERENCE RULE:
    IDRF should surface only dependencies supported by
    BOTH structural context and at least one metadata concern,
    or by multiple independent structural concerns.

    This prevents trivial one-metric flagging.
    """
    cards = []

    for _, row in metrics_df.iterrows():
        rules, profiles, triggers = rules_and_profiles(row)
        structural_count = sum(rule in {"HIGH_CENTRALITY", "TRANSITIVE_DEPENDENCY", "PROPAGATION_BREADTH", "SHARED_UPSTREAM_CONVERGENCE"} for rule in rules)
        metadata_count = sum(rule in {"STALE_MAINTENANCE", "MAINTAINER_CONCENTRATION", "LOW_ECOSYSTEM_VISIBILITY"} for rule in rules)

        score = investigative_priority(row)

        # ---------- final surfacing policy ----------
        if (structural_count >= 1 and metadata_count >= 1) or (structural_count >= 2):
            cards.append(
                InsightCard(
                    package=row.package,
                    investigative_priority_score=score,
                    finding="Dependency exhibits " + ", ".join(triggers) + ".",
                    rationale=f"Combined structural and metadata indicators suggest elevated investigative attention for {row.package}.",
                    recommended_question="Should this dependency be buffered, substituted, or explicitly monitored?",
                    evidence=evidence_for_row(row),
                    triggered_rules=rules,
                    investigation_profile=profiles,
                    confidence="moderate",
                )
            )

    cards.sort(key=lambda x: x.investigative_priority_score, reverse=True)
    return cards[:5]