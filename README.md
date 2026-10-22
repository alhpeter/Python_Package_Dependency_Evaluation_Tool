# Python Package Dependency Evaluation Tool

A Python-based tool for exploring the structure of Python package dependencies and identifying packages that may deserve closer maintenance or supply-chain review.

The tool reads `requirements.txt` manifests, retrieves public package metadata from PyPI, builds a bounded dependency graph, calculates graph and maintenance-related metrics, and produces ranked investigation cards. A local dashboard helps you explore the results, compare experiments, and understand why a package was flagged for review.

> **Important:** This is a research and decision-support tool, not a vulnerability scanner. A high priority score does not mean that a package is vulnerable, malicious, or unsafe. It means the available signals suggest that the package may be worth investigating sooner.

## At a glance

- **Input:** `requirements.txt` files describing the packages in a Python project.
- **Data sources:** PyPI package metadata and, when a project repository can be identified, public GitHub repository information.
- **Analysis:** A bounded directed dependency graph, graph metrics, maintenance signals, transparent rules, and a weighted priority score.
- **Results:** CSV metrics, JSON summaries and investigation cards, dependency graph images, and a browser-based dashboard.
- **Optional AI help:** A Groq-powered assistant explains already-generated results in plain language. The core analysis does not depend on AI.

## Why this tool exists

Python projects often depend on packages that depend on other packages. These indirect, or transitive, dependencies can be easy to overlook. A package may also sit in an important position in the dependency graph, have limited public activity information, or connect to several other packages.

The tool brings these signals together so a developer or researcher can ask better questions:

- Which packages sit in structurally important positions?
- How deep into the dependency tree does a package appear?
- What public maintenance or popularity signals are available?
- Which packages should be reviewed first, and what evidence supports that choice?

The goal is to support **human investigation**, not to make an automatic security decision.

## How it works

The analysis pipeline performs the evaluation. The optional Groq integration only explains results after the analysis has run.

1. **Load a project manifest.** The experiment runner maps experiment names to `requirements.txt` files. The configured runs include web/API/ML examples and nine external case studies. You can add or change an entry in `EXPERIMENTS` in `run_idrf.py` to evaluate another manifest.
2. **Retrieve package metadata.** Package names are normalized and queried against the public PyPI JSON API. The tool uses the available dependency metadata and filters out non-runtime dependency entries. Dependency discovery is deliberately bounded by configured depth and child limits, rather than crawling an unlimited package ecosystem.
3. **Build a dependency graph.** A synthetic `ROOT_PROJECT` node connects to the packages listed in the manifest. Dependency links connect those packages to the retained dependencies found in metadata. This makes both direct and selected transitive relationships easier to inspect.
4. **Calculate evaluation signals.** The tool records graph measures such as dependency depth, betweenness centrality, incoming links (`indegree`), and outgoing links (`outdegree`). It also uses available metadata such as GitHub stars, time since the last repository push, and a maintainer-count proxy. Some values may be unavailable or approximate when public metadata cannot be retrieved.
5. **Rank investigation candidates.** Transparent rules and a weighted **Investigative Priority Score (IPS)** combine structural influence, dependency depth, staleness, maintainer concentration, public visibility, and connectivity. The tool then creates ranked insight cards with evidence, triggered rules, investigation profiles, and suggested follow-up questions.
6. **Save the results.** Each experiment writes artifacts to its own `outputs/<experiment-name>/` directory. The dashboard reads these saved files; it does not launch the analysis itself.

### Understanding the priority score

The IPS is a **heuristic for ordering human review**. It is not a probability, a calibrated risk estimate, or a security rating. The score helps answer “What should I look at first?” rather than “Is this package unsafe?”

Public metadata is only a partial view of package health. Missing or outdated information can affect measurements, and the configured dependency-depth limits mean the graph is not a complete picture of every possible dependency.

## Setup (Windows, Linux, and macOS)

### 1. Get the project

Clone the repository or download and extract its ZIP archive. Open a terminal in the project root: the folder containing `requirements.txt`, `run_idrf.py`, and `dashboard_server.py`.

You will need Python 3 and an internet connection to retrieve public package metadata from PyPI. Check whether Python and pip are available:

```bash
python --version
python -m pip --version
```

On many Linux distributions, use `python3` instead of `python`. On Windows, install Python from [python.org](https://www.python.org/downloads/) and select **Add Python to PATH** during installation if that option is shown.

### 2. Create and activate a virtual environment

A virtual environment keeps this project's Python packages separate from other projects.

**Windows — Command Prompt (CMD):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**Windows — PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of its execution policy, you can use Command Prompt instead. Alternatively, for the current PowerShell session only, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then activate the environment again. Follow your organization's security policies on managed computers.

**Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If creating a virtual environment fails because `venv` is unavailable, install the Python venv package through your distribution's package manager. For example, on Ubuntu or Debian:

```bash
sudo apt update
sudo apt install python3-venv
```

**macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When activation succeeds, your terminal will usually show `(.venv)` at the beginning of the prompt.

### 3. Install project dependencies

With the virtual environment activated, run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Linux or macOS, if your environment uses `python3` rather than `python`, you can use `python3 -m pip` for these commands.

The requirements file installs the libraries used by the project, including NetworkX for graph analysis, pandas for tabular data, Matplotlib for graph images, Requests for HTTP requests, Flask for the dashboard, and python-dotenv for local environment variables.

## Run an evaluation

From the project root, run:

```bash
python run_idrf.py
```

The runner executes the experiments configured in `EXPERIMENTS`, prints progress and a summary, and saves detailed results under `outputs/`. It also creates:

```text
outputs/cross_experiment_summary.json
```

To evaluate a different manifest, edit the `EXPERIMENTS` mapping in `run_idrf.py`. Use a path to the relevant `requirements.txt` file, relative to the project root. Keep the configured depth and child limits in mind: the tool intentionally evaluates a bounded portion of the dependency graph.

> **Naming note:** The project is presented as the **Python Package Dependency Evaluation Tool**, but some existing implementation files and Python imports still use the original `idrf` name, including `run_idrf.py` and the `idrf/` package directory. The commands above match the current code.

## Open the dashboard

First run an evaluation so the output files exist. Then start the local Flask server:

```bash
python dashboard_server.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The dashboard lets you select an experiment and inspect:

- an overview and experiment summary;
- the ranked investigation queue;
- package-level metrics and supporting evidence;
- the dependency graph;
- priority-score components and triggered rules; and
- comparisons across experiments.

The dashboard reads existing files in `outputs/`. If no experiments have been run, or the expected output artifacts are missing, run `python run_idrf.py` first.

## Optional: enable the AI results guide

The dashboard includes two optional AI-assisted features:

- **Ask the AI guide:** Ask questions about the selected experiment, its metrics, scores, packages, insight cards, or graph.
- **Explain a package:** Request a plain-language explanation of a package's recorded evidence, score components, triggered rules, and investigation profile, along with questions that may guide further review.

The current integration uses the `openai/gpt-oss-20b` model through Groq's chat completions API. It explains data that the tool has already generated; it does not run evaluations, inspect your local project files, browse the web, or change the analysis results. AI responses can be inaccurate and should not be treated as security verdicts.

### Configure the API key

Create a file named `.env` in the project root and add your own Groq API key:

```text
GROQ_API_KEY=your-groq-key
```

The dashboard server loads this file automatically. Keep the key private and do not commit it to version control. The key remains on the server rather than being sent to the browser. However, when you use the AI features, your questions, conversation history, and the selected experiment's result data are sent to Groq to generate a response.

The core analysis and dashboard results remain usable without the API key. If the key is missing or the service is unavailable, the AI features will be unavailable.

## Output files

For each experiment, the tool generates the following files under `outputs/<experiment-name>/`:

| File | What it contains |
|---|---|
| `metrics.csv` | Package-level graph and metadata measurements. |
| `insights.json` | Ranked investigation cards, scores, evidence, and suggested follow-up questions. |
| `experimental_summary.json` | Aggregate counts and summary metrics for the experiment. |
| `dependency_graph.png` | A visual representation of the bounded dependency graph. |

The cross-experiment summary at `outputs/cross_experiment_summary.json` provides a compact comparison of the configured runs.

## Project structure

```text
.
├── data/                  # Example manifests and external case studies
├── dashboard/             # Browser dashboard assets
├── docs/                  # Methodology, architecture, and experiment notes
├── idrf/                  # Core analysis and graph-evaluation modules
├── outputs/               # Generated experiment artifacts (created at runtime)
├── requirements.txt       # Python dependencies
├── run_idrf.py            # Runs the configured experiments
└── dashboard_server.py    # Serves the local dashboard and optional AI guide
```

## Scope and limitations

- The analysis uses public package and repository metadata available at run time.
- Dependency discovery is intentionally bounded; the graph may not include every dependency in the wider ecosystem.
- Network failures or missing metadata can lead to fallback values or approximate measurements.
- The maintainer count is a proxy based on available information, not a definitive measure of maintainer health.
- The score uses explicit rules and weighted signals. It is not a machine-learning prediction.
- The tool does not identify known CVEs, prove exploitability, determine whether a package is malicious, recommend package replacements automatically, or continuously monitor CI/CD pipelines.

Use the results as a starting point for review. Check package documentation, release history, repository activity, and trusted security advisories before making a dependency decision.


## Team Members

Listed alphabetically by first name:

1. **Aleena Harold Peter** (`1GD23IS006`)
2. **Pratiksha Pranesh Joshi** (`1GD23IS041`)
3. **Syeda Hajira Misbah** (`1GD23IS056`)
4. **Thanya Aiyappa T** (`1GD23IS057`)

## Under the Guidance of

**Sreelatha Mutyala**  
Assistant Professor  
Department of Information Science and Engineering (ISE)

## Acknowledgements

We sincerely thank **Dr. Madhusmita Das** for her guidance and support during the sixth semester, and for helping us bring this project to fruition. We are also grateful to **Sreelatha Mutyala**, our guide for the seventh semester, for her continued guidance, feedback, and support as we developed the project.

