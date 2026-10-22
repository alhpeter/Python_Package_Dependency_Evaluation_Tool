# Investigative Dependency Reasoning Framework (IDRF)

[![Wiki](https://img.shields.io/badge/Wiki-Project%20Handbook-blue)](https://github.com/aleenaharoldpeter/INVESTIGATIVE-DEPENDENCY-REASONING-FRAMEWORK/wiki)

An analytical system for software dependency ecosystems that combines graph-based structural analysis with investigative reasoning to identify risk patterns, information gaps, and interpretable insights for human-in-the-loop decision support.

IDRF is a reasoning-first tool that analyzes software dependency graphs, highlights structural risk patterns, and generates investigative prompts to support human decision-making.

## Project Handbook (Wiki)

A human-friendly handbook, design docs, and meeting notes are maintained in the project Wiki:  
👉 [Wiki](https://github.com/aleenaharoldpeter/INVESTIGATIVE-DEPENDENCY-REASONING-FRAMEWORK/wiki)

Use the Wiki for:
- Roadmap
- How to run
- Pattern Catalog
- Evaluation results
- Weekly Notes

## Research Focus

This project investigates:
- How structural properties of software dependency graphs correlate with maintenance and supply-chain risk.
- How raw graph metrics can be transformed into interpretable reasoning patterns and investigative prompts for developers.

## What this is not

> IDRF is not a vulnerability scanner or prediction model.  
> It is a reasoning-first analytical framework intended to support human investigation and decision-making.

## How the project works

IDRF separates its evidence-based analysis from its optional AI explanations. The
analysis pipeline—not Groq—builds the dependency graph, calculates metrics,
assigns priority scores, and selects investigation candidates.

1. **Load experiment manifests.** ``run_idrf.py`` contains the ``EXPERIMENTS``
   mapping of experiment names to ``requirements.txt`` files. It currently runs
   the ``web``, ``ml``, and ``api`` examples plus nine external case studies.
   Add or change a mapping there to run a different manifest.
2. **Collect bounded package data.** IDRF normalizes package names from each
   manifest and queries the public PyPI JSON API for package dependency metadata.
   It filters non-runtime dependency entries and limits how many dependency
   levels and children are included, keeping each experiment bounded. When PyPI
   provides a GitHub project link, IDRF also retrieves public repository stars
   and last-push time. Network lookups use timeouts; unavailable metadata falls
   back to defaults, so some measurements may be approximate.
3. **Build and measure the graph.** A directed graph connects a synthetic
   ``ROOT_PROJECT`` to the manifest's packages and those packages to the
   dependency links retained from metadata. IDRF calculates package depth,
   betweenness centrality, incoming and outgoing links, and metadata signals
   such as stars, time since last update, and a maintainer-count proxy.
4. **Prioritize for human review.** Transparent rules and a weighted
   Investigative Priority Score (IPS) combine structural influence, dependency
   depth, maintenance freshness, maintainer concentration, public visibility,
   and connectivity. IDRF uses these results to create ranked insight cards
   with supporting evidence, triggered rules, investigation profiles, and a
   suggested follow-up question.
5. **Save experiment artifacts.** Each run writes its results to its own
   ``outputs/<experiment-name>/`` directory. The dashboard reads these saved
   artifacts; it does not rerun the analysis.

The score is a prioritization heuristic, not a probability or security rating.
IDRF can highlight patterns that merit investigation, but it does not determine
that a package is vulnerable, malicious, or unsafe.

## Setup and run an analysis

From the project root, install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Run all experiments listed in ``run_idrf.py``:

```bash
python run_idrf.py
```

The runner prints progress and a summary for each experiment, then writes a
cross-experiment summary to ``outputs/cross_experiment_summary.json``.

## Run the dashboard

After the experiment artifacts have been generated, start the local Flask
dashboard from the project root:

```bash
python dashboard_server.py
```

Open http://127.0.0.1:5000. Select an experiment to explore its overview,
priority queue, package evidence, dependency graph, score breakdown, and
cross-experiment comparison. The optional **Take the 2-minute tour** explains
how to read these sections. The dashboard needs existing output artifacts; it
does not start an analysis run.

## Groq-powered AI results guide

The dashboard includes an optional, conversational AI assistant for explaining
the currently selected experiment:

- **Ask the AI guide** about the experiment, metrics, scores, packages, insight
  cards, or graph. The server sends the conversation and a data bundle for the
  selected experiment—including its summary, score guide, package metrics, and
  insight cards—to Groq's chat completions API. Replies are displayed in the
  dashboard and can include Markdown.
- **Explain a package** requests a structured plain-language explanation of a
  surfaced package's existing evidence, score components, rules, and
  investigation profile, along with suggested questions for further
  investigation.

The integration currently calls Groq with the ``openai/gpt-oss-20b`` model.
This assistant only explains data IDRF has already produced: it cannot run an
analysis, inspect local project files, browse the web, or change scores or
files. Its answers can be wrong and are not security verdicts.

Set ``GROQ_API_KEY`` in the environment of the dashboard server. For local
development, create a project-root ``.env`` file containing:

```text
GROQ_API_KEY=your-groq-key
```

The server loads this file automatically. Keep it private; ``.env`` is ignored
by Git. The key stays on the server and is not sent to the browser. User
questions, conversation history, and the selected experiment's result data are
sent to Groq to generate responses. If the key is missing or Groq is
unavailable, the analysis results and the rest of the dashboard remain usable;
the AI features report that they are unavailable.

## Outputs

For each experiment, IDRF writes:

- ``metrics.csv`` — package-wise graph and metadata measurements.
- ``insights.json`` — ranked investigation cards with scores, evidence, and
  suggested next questions.
- ``experimental_summary.json`` — aggregate counts and summary metrics.
- ``dependency_graph.png`` — a visualization of the bounded dependency graph.

The dashboard consumes these files, and ``outputs/cross_experiment_summary.json``
provides a comparison across the experiments run by the configured runner.

## Reproducibility and scope

The experiment manifests, analysis rules, configuration, and research notes are
available in this repository and the project Wiki. The pipeline uses public
package and repository metadata and intentionally limits dependency discovery;
results therefore reflect the data available at run time and the configured
bounds.

IDRF is a research and decision-support prototype. It is not an industrial-scale
dependency crawler, vulnerability scanner, machine-learning prediction system,
automated package replacement recommender, or real-time CI/CD monitor. A high
IPS means “look here sooner,” not “this package is unsafe.”

## Team
- [Aleena Harold Peter](https://www.linkedin.com/in/aleena-harold-peter/) <!-- — data collection & preprocessing -->
- Teammate A <!-- — data collection & preprocessing -->
- Teammate B <!-- — graph analytics & metrics -->
- Teammate C <!-- — visualization & evaluation -->

## Faculty Advisor
- [Dr. Madhusmita Das](https://www.linkedin.com/in/dr-madhusmita-das-phd-nitk-94613077), Department of ISE, Gopalan College of Engineering and Management


## Contacts
- Aleena Harold Peter  <br>[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/aleenaharoldpeter)  [![Gmail](https://img.shields.io/badge/Gmail-Contact-red?logo=gmail)](mailto:aleenaharoldpeter120@gmail.com)  [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077b5?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0nMjU2JyBoZWlnaHQ9JzI1NicgeG1sbnM9J2h0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnJyBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSd4TWlkWU1pZCcgdmlld0JveD0nMCAwIDI1NiAyNTYnPjxwYXRoIGQ9J00yMTguMTIzIDIxOC4xMjdoLTM3LjkzMXYtNTkuNDAzYzAtMTQuMTY1LS4yNTMtMzIuNC0xOS43MjgtMzIuNC0xOS43NTYgMC0yMi43NzkgMTUuNDM0LTIyLjc3OSAzMS4zNjl2NjAuNDNoLTM3LjkzVjk1Ljk2N2gzNi40MTN2MTYuNjk0aC41MWEzOS45MDcgMzkuOTA3IDAgMCAxIDM1LjkyOC0xOS43MzNjMzguNDQ1IDAgNDUuNTMzIDI1LjI4OCA0NS41MzMgNTguMTg2bC0uMDE2IDY3LjAxM1pNNTYuOTU1IDc5LjI3Yy0xMi4xNTcuMDAyLTIyLjAxNC05Ljg1Mi0yMi4wMTYtMjIuMDA5LS4wMDItMTIuMTU3IDkuODUxLTIyLjAxNCAyMi4wMDgtMjIuMDE2IDEyLjE1Ny0uMDAzIDIyLjAxNCA5Ljg1MSAyMi4wMTYgMjIuMDA4QTIyLjAxMyAyMi4wMTMgMCAwIDEgNTYuOTU1IDc5LjI3bTE4Ljk2NiAxMzguODU4SDM3Ljk1Vjk1Ljk2N2gzNy45N3YxMjIuMTZaTTIzNy4wMzMuMDE4SDE4Ljg5QzguNTgtLjA5OC4xMjUgOC4xNjEtLjAwMSAxOC40NzF2MjE5LjA1M2MuMTIyIDEwLjMxNSA4LjU3NiAxOC41ODIgMTguODkgMTguNDc0aDIxOC4xNDRjMTAuMzM2LjEyOCAxOC44MjMtOC4xMzkgMTguOTY2LTE4LjQ3NFYxOC40NTRjLS4xNDctMTAuMzMtOC42MzUtMTguNTg4LTE4Ljk2Ni0xOC40NTMnIGZpbGw9JyNmZmYnLz48L3N2Zz4K)](https://www.linkedin.com/in/aleena-harold-peter/)