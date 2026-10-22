"""Single runnable experiment entrypoint for reproducible IDRF execution."""
from idrf.pipeline import run_idrf
from idrf.reporting import TerminalReporter

# if __name__=='__main__':
#     metrics,cards,summary=run_idrf('data/flask_app_requirements.txt')
#     print(metrics.to_string(index=False))
#     print(summary)
#     for c in cards:
#         print(c)
#         print("-" * 80)

#     print("\n================ EXPERIMENTAL SUMMARY ================\n")
#     print(summary)

# from idrf.pipeline import run_idrf

# if __name__ == "__main__":
#     metrics, cards, summary = run_idrf("data/flask_app_requirements.txt")

#     print("\n================ TOP METRIC SNAPSHOT ================\n")
#     print(metrics.head(10).to_string(index=False))

#     print("\n================ TOP INSIGHT CARDS ================\n")
#     for c in cards:
#         print(c)
#         print("-" * 80)

#     print("\n================ EXPERIMENTAL SUMMARY ================\n")
#     print(summary)

"""
Single reproducible bounded experiment runner for IDRF.
Terminal output is intentionally concise; detailed artifacts are written to outputs/.
"""

# from idrf.pipeline import run_idrf

# if __name__ == "__main__":
#     metrics, cards, summary = run_idrf("data/flask_app_requirements.txt")

#     print("\n================ IDRF EXECUTION COMPLETE ================\n")
#     print("Analyzed Packages :", len(metrics))
#     print("Generated Cards   :", len(cards))
#     print("Max Priority Score:", summary["max_investigative_score"])

#     print("\nTop 5 Investigative Dependencies:\n")
#     for c in cards[:5]:
#         print(c)
#         print("-" * 80)

#     print("\nExperimental Summary:\n")
#     print(summary)

#     print("\nDetailed CSV/JSON/Graph artifacts saved in outputs/ directory.\n")





# """
# Multi-experiment reproducible bounded runner for IDRF.

# Grounding:
# One-run demonstration is insufficient for proposal-level validation.
# This runner executes three controlled ecosystems to provide bounded
# comparative evidence for CIE53 reporting.
# """

# from idrf.pipeline import run_idrf

# EXPERIMENTS = {
#     "web": "data/api_service_requirements.txt",
#     "ml": "data/flask_app_requirements.txt",
#     "security": "data/ml_stack_requirements.txt"
# }


# if __name__ == "__main__":

#     cross_summary = []

#     for exp_name, req_file in EXPERIMENTS.items():
#         metrics, cards, summary = run_idrf(req_file, exp_name)

#         print(f"\n================ IDRF EXECUTION COMPLETE [{exp_name.upper()}] ================\n")
#         print("Analyzed Packages :", len(metrics))
#         print("Generated Cards   :", len(cards))
#         print("Max Priority Score:", summary["max_investigative_score"])

#         print("\nTop Investigative Dependencies:\n")
#         for c in cards[:5]:
#             print(c)
#             print("-" * 80)

#         print("\nExperimental Summary:\n")
#         print(summary)

#         cross_summary.append({
#             "experiment": exp_name,
#             "packages_analyzed": summary["total_packages_analyzed"],
#             "cards_generated": summary["high_priority_dependencies"],
#             "max_score": summary["max_investigative_score"]
#         })

#     print("\n================ CROSS EXPERIMENT SUMMARY ================\n")
#     for row in cross_summary:
#         print(row)

#     print("\nDetailed artifacts saved under outputs/web outputs/ml outputs/security\n")










"""
Multi-experiment reproducible bounded runner for IDRF.

Grounding:
One-run demonstration is insufficient for proposal-level validation.
This runner executes three controlled ecosystems to provide bounded
comparative evidence for CIE53 reporting.
"""

from idrf.pipeline import run_idrf
import os
import json

EXPERIMENTS = {
    "web": "data/flask_app_requirements.txt",
    "ml": "data/ml_stack_requirements.txt",
    "api": "data/api_service_requirements.txt",
    # ---------------------------------------------------
    # EXTERNAL REAL-WORLD CASE STUDIES
    # ---------------------------------------------------
    "airflow_case": "data/external_cases/case_airflow_orchestration.txt.txt",
    "celery_case": "data/external_cases/case_celery_distributed_queue.txt.txt",
    "fastapi_case": "data/external_cases/case_fastapi_modern_api.txt.txt",
    "flask_case": "data/external_cases/case_flask_mature_web.txt.txt",
    "greatexpectations_case": "data/external_cases/case_greatexpectations_datavalidation.txt.txt",
    "kedro_case": "data/external_cases/case_kedro_mlops.txt.txt",
    "prefect_case": "data/external_cases/case_prefect_workflow.txt.txt",
    "scrapy_case": "data/external_cases/case_scrapy_crawler.txt.txt",
    "streamlit_case": "data/external_cases/case_streamlit_appframework.txt.txt"
}

if False and __name__ == "__main__":

    cross_summary = []

    for exp_name, req_file in EXPERIMENTS.items():
        metrics, cards, summary = run_idrf(req_file, exp_name)

        print(f"\n================ IDRF EXECUTION COMPLETE [{exp_name.upper()}] ================\n")
        print("Analyzed Packages :", len(metrics))
        print("Generated Cards   :", len(cards))
        print("Max Priority Score:", summary["max_investigative_score"])

        print("\nTop Investigative Dependencies:\n")
        for c in cards[:5]:
            print(c)
            print("-" * 80)

        print("\nExperimental Summary:\n")
        print(summary)

        cross_summary.append({
            "experiment": exp_name,
            "packages_analyzed": summary["total_packages_analyzed"],
            "cards_generated": summary["high_priority_dependencies"],
            "max_score": summary["max_investigative_score"]
        })

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/cross_experiment_summary.json", "w", encoding="utf-8") as f:
        json.dump(cross_summary, f, indent=2)

    print("\n================ CROSS EXPERIMENT SUMMARY ================\n")
    for row in cross_summary:
        print(row)

    print("\nDetailed artifacts saved under outputs/web outputs/ml outputs/api\n")


def run_experiment_with_report(experiment_name, requirements_path):
    reporter = TerminalReporter(requirements_path, experiment_name)
    reporter.startup()
    try:
        metrics, cards, summary = run_idrf(
            requirements_path,
            experiment_name,
            progress_callback=reporter.progress,
        )
    except Exception as error:
        reporter.failure(reporter.current_stage, error)
        raise

    reporter.summary(metrics, cards)
    reporter.candidates(cards)
    reporter.reasoning(cards)
    reporter.artifacts(experiment_name)
    reporter.complete()
    return metrics, cards, summary


if __name__ == "__main__":
    cross_summary = []
    for exp_name, req_file in EXPERIMENTS.items():
        metrics, cards, summary = run_experiment_with_report(exp_name, req_file)
        cross_summary.append({
            "experiment": exp_name,
            "packages_analyzed": summary["total_packages_analyzed"],
            "cards_generated": summary["high_priority_dependencies"],
            "max_score": summary["max_investigative_score"],
        })

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/cross_experiment_summary.json", "w", encoding="utf-8") as handle:
        json.dump(cross_summary, handle, indent=2)

    print("\n" + "─" * 68)
    print("CROSS-EXPERIMENT SUMMARY")
    print("─" * 68)
    for row in cross_summary:
        print(
            f"{row['experiment']}: {row['packages_analyzed']} packages, "
            f"{row['cards_generated']} insight cards, max score {row['max_score']:.3f}"
        )