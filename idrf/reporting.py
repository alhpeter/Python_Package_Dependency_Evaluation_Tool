"""Human-facing terminal reporting for reproducible IDRF experiments."""
from datetime import datetime
from pathlib import Path
import os
import sys

from .config import MAX_TRANSITIVE_DEPTH


STAGES = {
    1: "Loading manifest and resolving metadata",
    2: "Building dependency graph",
    3: "Computing structural metrics",
    4: "Applying investigative reasoning",
    5: "Writing CSV and JSON artifacts",
    6: "Generating dependency graph image",
    7: "Writing experiment summary",
}


class TerminalReporter:
    """Render progress and factual summaries without calculating analysis."""

    def __init__(self, requirements_path, experiment_name):
        self.requirements_path = requirements_path
        self.experiment_name = experiment_name
        self.run_id = f"IDRF-{datetime.now():%Y-%m-%d-%H%M%S}"
        self.started_at = datetime.now()
        self.use_color = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
        self.current_stage = 1

    def color(self, text, code):
        return f"\033[{code}m{text}\033[0m" if self.use_color else text

    def section(self, title):
        print("\n" + "─" * 68)
        print(title)
        print("─" * 68)

    def startup(self):
        print("╔" + "═" * 66 + "╗")
        print("║" + "INVESTIGATIVE DEPENDENCY REASONING FRAMEWORK".center(66) + "║")
        print("║" + "IDRF".center(66) + "║")
        print("╠" + "═" * 66 + "╣")
        print("║" + "Dependency Ecosystem Investigation & Reasoning".center(66) + "║")
        print("║" + "Transparent • Evidence-Based • Reproducible".center(66) + "║")
        print("╚" + "═" * 66 + "╝")
        self.section("RUN METADATA")
        print(f"Run ID        : {self.run_id}")
        print(f"Timestamp     : {self.started_at:%Y-%m-%d %H:%M:%S}")
        print(f"Experiment    : {self.experiment_name}")
        print(f"Target        : {self.requirements_path}")
        print("Analysis      : Dependency Ecosystem Investigation")
        print(f"Depth bound   : {MAX_TRANSITIVE_DEPTH}")
        print("Reasoning     : Transparent Heuristic")

    def progress(self, stage, status):
        label = STAGES[stage]
        self.current_stage = stage
        if status == "start":
            print(f"[{stage:02d}/07] {label} ...", end="", flush=True)
        else:
            print(" " + self.color("✓", "32"))

    def failure(self, stage, error):
        print(" " + self.color("✗", "31"))
        print(f"Reason: {type(error).__name__}: {error}")

    def summary(self, metrics, cards):
        self.section("ANALYSIS SUMMARY")
        print(f"Packages analyzed       : {len(metrics)}")
        print(f"Dependency links        : {int(metrics['indegree'].sum())}")
        print(f"Graph nodes             : {len(metrics) + 1}")
        print(f"Graph edges             : {int(metrics['indegree'].sum())}")
        print(f"Maximum depth           : {int(metrics['depth'].max()) if len(metrics) else 0}")
        print(f"Triggered rule signals  : {sum(len(card.triggered_rules) for card in cards)}")
        print(f"Investigation candidates: {len(cards)}")
        print(f"Insight cards generated : {len(cards)}")

    def candidates(self, cards):
        self.section("TOP INVESTIGATION CANDIDATES")
        if not cards:
            print("No investigation candidates were generated.")
            return
        for index, card in enumerate(cards[:5], 1):
            profile = " + ".join(card.investigation_profile) or "Not classified"
            evidence = card.finding.removeprefix("Dependency exhibits ").rstrip(".")
            print(f"{index}. {card.package}")
            print(f"   Priority score : {card.investigative_priority_score:.3f}")
            print(f"   Profile        : {profile}")
            print(f"   Evidence       : {evidence}")

    def reasoning(self, cards):
        self.section("INVESTIGATIVE REASONING")
        for card in cards[:3]:
            print(f"Package: {card.package}")
            print(f"Priority score: {card.investigative_priority_score:.3f}")
            print("Evidence:")
            for key, value in card.evidence.items():
                if key != "score_components":
                    print(f"  {key.replace('_', ' ').title():24} {value}")
            print("Score components:")
            for key, value in card.evidence.get("score_components", {}).items():
                print(f"  {key.replace('_', ' ').title():24} {value}")
            print("Triggered rules:")
            for rule in card.triggered_rules:
                print(f"  {self.color('✓', '32')} {rule}")
            print("Investigation profile:")
            for profile in card.investigation_profile:
                print(f"  {self.color('→', '36')} {profile}")
            print(f"Recommended investigation: {card.recommended_question}")
            print()

    def artifacts(self, experiment_name):
        output_dir = Path("outputs") / experiment_name
        self.section("RESEARCH ARTIFACTS")
        for name in ("metrics.csv", "insights.json", "experimental_summary.json", "dependency_graph.png"):
            path = output_dir / name
            marker = self.color("✓", "32") if path.exists() else self.color("✗", "31")
            print(f"{marker} {path}")
        print(f"\nOutput directory: {output_dir}/")

    def complete(self):
        self.section("REPRODUCIBILITY STATUS")
        for item in ("Dependency analysis completed", "Metrics generated", "Reasoning rules evaluated", "Insight cards generated", "Research artifacts written"):
            print(f"{self.color('✓', '32')} {item}")
        print(f"\nRun ID: {self.run_id}")
        print("Run completed successfully.")