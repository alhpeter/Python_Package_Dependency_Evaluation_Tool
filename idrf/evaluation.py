# import os, json
# from dataclasses import asdict
# import pandas as pd

# from idrf.models import InsightCard
# from typing import List


# def export_results(metrics:pd.DataFrame,cards:List[InsightCard]):
#     """
#     Export reproducibility artifacts.

#     WHY THIS FUNCTION EXISTS:
#     Conference papers require tables that can be regenerated. CSV and JSON
#     outputs provide direct traceability from computation to reported results.
#     """
#     os.makedirs('outputs',exist_ok=True)
#     metrics.to_csv('outputs/metrics.csv',index=False)
#     with open('outputs/insights.json','w',encoding='utf-8') as f:
#         json.dump([asdict(c) for c in cards],f,indent=2)


# def generate_experimental_summary(metrics:pd.DataFrame,cards:List[InsightCard]):
#     """
#     Generate compact quantitative summary statistics.

#     WHY THIS FUNCTION EXISTS:
#     This function creates immediately reportable experimental numbers for the
#     Results and Evaluation sections without manual recomputation.
#     """
#     summary={
#         'total_packages_analyzed':int(len(metrics)),
#         'mean_centrality':float(round(metrics['centrality'].mean(),4)),
#         'mean_depth':float(round(metrics['depth'].mean(),4)),
#         'high_priority_dependencies':int(len(cards)),
#         'max_investigative_score':float(max([c.investigative_priority_score for c in cards],default=0))
#     }
#     with open('outputs/experimental_summary.json','w',encoding='utf-8') as f:
#         json.dump(summary,f,indent=2)
# import os
# import json
# from dataclasses import asdict
# import pandas as pd
# from typing import List
# from idrf.models import InsightCard


# def export_results(metrics: pd.DataFrame, cards: List[InsightCard]):
#     """
#     Export all reproducibility artifacts required for paper tables and appendix.
#     """
#     os.makedirs("outputs", exist_ok=True)

#     metrics.to_csv("outputs/metrics.csv", index=False)

#     with open("outputs/insights.json", "w", encoding="utf-8") as f:
#         json.dump([asdict(c) for c in cards], f, indent=2)


# def generate_experimental_summary(metrics: pd.DataFrame, cards: List[InsightCard]):
#     """
#     Generate compact experimental summary for Results section reporting.
#     """
#     summary = {
#         "total_packages_analyzed": int(len(metrics)),
#         "mean_centrality": float(round(metrics["centrality"].mean(), 4)),
#         "mean_depth": float(round(metrics["depth"].mean(), 4)),
#         "high_priority_dependencies": int(len(cards)),
#         "max_investigative_score": float(max([c.investigative_priority_score for c in cards], default=0))
#     }

#     with open("outputs/experimental_summary.json", "w", encoding="utf-8") as f:
#         json.dump(summary, f, indent=2)

#     return summary




import os
import json
from dataclasses import asdict
import pandas as pd
from typing import List
from idrf.models import InsightCard


def export_results(metrics: pd.DataFrame, cards: List[InsightCard], output_dir: str):
    """
    Export reproducibility artifacts for a specific bounded experiment.

    WHY:
    Proposal Section 5.4 requires preserved per-experiment evidence rather than
    overwritten single-run outputs.
    """
    os.makedirs(output_dir, exist_ok=True)

    metrics.to_csv(os.path.join(output_dir, "metrics.csv"), index=False)

    with open(os.path.join(output_dir, "insights.json"), "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in cards], f, indent=2)


def generate_experimental_summary(metrics: pd.DataFrame, cards: List[InsightCard], output_dir: str):
    """
    Generate compact reportable quantitative summary for one experiment.
    """
    summary = {
        "total_packages_analyzed": int(len(metrics)),
        "mean_centrality": float(round(metrics["centrality"].mean(), 4)),
        "mean_depth": float(round(metrics["depth"].mean(), 4)),
        "high_priority_dependencies": int(len(cards)),
        "max_investigative_score": float(max([c.investigative_priority_score for c in cards], default=0))
    }

    with open(os.path.join(output_dir, "experimental_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
