# import re
# import requests
# from urllib.parse import urlparse
# from datetime import datetime, timezone
# from typing import List, Dict, Optional, Set
# from .models import PackageNode
# from .config import MAX_TRANSITIVE_DEPTH, REQUEST_TIMEOUT, GITHUB_API

# def clean_package_name(raw:str)->str:
#     """
#     Sanitize raw dependency strings into valid package identifiers.

#     WHY THIS FUNCTION IS NECESSARY:
#     PyPI requires_dist entries often contain:
#     - version constraints,
#     - optional extras,
#     - environment markers.
#     Querying those raw strings directly would create invalid API requests.
#     This cleaner prevents malformed crawl behavior and stabilizes recursion.
#     """
#     raw = raw.split(';')[0]
#     raw = raw.split('[')[0]
#     raw = re.split(r'[<>=!~() ]+', raw)[0]
#     return raw.strip()

# def extract_dependencies(requirements_path:str)->List[str]:
#     """
#     Extract direct root dependencies from a local requirements manifest.

#     WHY THIS FUNCTION EXISTS:
#     This is the concrete implementation of GitHub issue #14.
#     The local manifest serves as the experimentally controllable entry point
#     into the dependency ecosystem under investigation.
#     """
#     deps=[]
#     with open(requirements_path,'r',encoding='utf-8') as f:
#         for line in f:
#             line=line.strip()
#             if line and not line.startswith('#'):
#                 pkg=clean_package_name(line)
#                 if pkg:
#                     deps.append(pkg)
#     return deps

# def fetch_pypi_full(package_name:str)->Dict:
#     """
#     Retrieve full public package metadata from PyPI JSON API.

#     WHY THIS FUNCTION EXISTS:
#     The proposal explicitly claims metadata-aware dependency analysis rather than
#     pure graph topology. PyPI provides a reproducible public metadata source.

#     WHY requires_dist IS COLLECTED:
#     GitHub issue #15 requires transitive dependency closure, and requires_dist is
#     the only public lightweight way to recursively discover child packages.

#     WHY maintainer_count IS A PROXY:
#     PyPI does not expose a trustworthy contributor census. Therefore author field
#     availability is used conservatively as a maintainer concentration indicator,
#     and this must be acknowledged in the paper as a proxy approximation.
#     """
#     try:
#         r=requests.get(f'https://pypi.org/pypi/{package_name}/json',timeout=REQUEST_TIMEOUT)
#         if r.status_code!=200:
#             return {}
#         info=r.json().get('info',{})
#         reqs=info.get('requires_dist') or []
#         reqs=[clean_package_name(x) for x in reqs if clean_package_name(x)]
#         maint_proxy = 1 if info.get('author') else 2
#         return {
#             'pypi_version':info.get('version','unknown'),
#             'summary':info.get('summary',''),
#             'author':info.get('author','unknown'),
#             'license':info.get('license','unknown'),
#             'homepage':info.get('home_page') or info.get('project_url') or '',
#             'requires_dist':reqs,
#             'maintainer_count':maint_proxy
#         }
#     except:
#         return {}

# def parse_github_repo(homepage_url:str)->Optional[str]:
#     """
#     Extract owner/repository slug from GitHub homepage links when available.

#     WHY THIS FUNCTION EXISTS:
#     PyPI alone cannot provide repository stars or push recency. This parser acts
#     as the bridge from package metadata to repository vitality enrichment.
#     """
#     if 'github.com' not in homepage_url.lower():
#         return None
#     try:
#         parts=urlparse(homepage_url).path.strip('/').split('/')
#         if len(parts)>=2:
#             return f"{parts[0]}/{parts[1]}"
#     except:
#         pass
#     return None

# def fetch_github_metadata(repo_slug:Optional[str])->Dict:
#     """
#     Fetch bounded repository vitality metadata from GitHub.

#     COLLECTED FIELDS:
#     - stars -> public visibility proxy
#     - open_issues -> unresolved maintenance load proxy
#     - last_update_days -> maintenance freshness proxy

#     WHY FALLBACK VALUES EXIST:
#     Many packages do not expose valid GitHub links. Instead of returning null and
#     breaking downstream metrics, conservative fallback values preserve stable
#     execution while avoiding exaggerated positive assumptions.
#     """
#     if not repo_slug:
#         return {'stars':10,'open_issues':0,'last_update_days':365}
#     try:
#         r=requests.get(GITHUB_API+repo_slug,timeout=REQUEST_TIMEOUT)
#         if r.status_code!=200:
#             return {'stars':10,'open_issues':0,'last_update_days':365}
#         d=r.json()
#         pushed=d.get('pushed_at')
#         delta=365
#         if pushed:
#             dt=datetime.strptime(pushed,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
#             delta=(datetime.now(timezone.utc)-dt).days
#         return {
#             'stars':d.get('stargazers_count',10),
#             'open_issues':d.get('open_issues_count',0),
#             'last_update_days':delta
#         }
#     except:
#         return {'stars':10,'open_issues':0,'last_update_days':365}

# def build_package_nodes(requirements_path:str)->Dict[str,PackageNode]:
#     """
#     Perform bounded recursive ETL over direct and transitive dependencies.

#     WHY THIS FUNCTION EXISTS:
#     This is the realization of GitHub issue #15 and the proposal's requirement
#     for ecosystem-level dependency understanding instead of flat direct lists.

#     WHY RECURSION IS BOUNDED:
#     Unlimited dependency closure can expand uncontrollably and crash conference
#     pilot runs. MAX_TRANSITIVE_DEPTH intentionally trades industrial completeness
#     for reproducible bounded experimentation.
#     """
#     discovered={}
#     visited=set()
#     def crawl(pkg:str,depth:int):
#         if pkg in visited or depth>MAX_TRANSITIVE_DEPTH:
#             return
#         visited.add(pkg)
#         pypi=fetch_pypi_full(pkg)
#         repo=parse_github_repo(pypi.get('homepage',''))
#         gh=fetch_github_metadata(repo)
#         deps=pypi.get('requires_dist',[])
#         discovered[pkg]=PackageNode(
#             name=pkg,
#             dependencies=deps,
#             pypi_version=pypi.get('pypi_version','unknown'),
#             summary=pypi.get('summary',''),
#             author=pypi.get('author','unknown'),
#             license=pypi.get('license','unknown'),
#             homepage=pypi.get('homepage',''),
#             stars=gh.get('stars',10),
#             open_issues=gh.get('open_issues',0),
#             last_update_days=gh.get('last_update_days',365),
#             maintainer_count=pypi.get('maintainer_count',1)
#         )
#         for child in deps:
#             crawl(child,depth+1)
#     for dep in extract_dependencies(requirements_path):
#         crawl(dep,0)
#     return discovered

# """
# IDRF Data Processing Module (V4 Bounded Conference Prototype)
# -------------------------------------------------------------

# WHY THIS MODULE EXISTS
# ----------------------
# This module implements the ETL layer described in:

# - Proposal Section 5.1 (Data Source and Scope)
# - GitHub Issues #3, #14, #15, #16

# The objective is NOT to crawl the full PyPI universe.
# The objective is to construct a controlled analytical dependency context around
# the analyst-provided root packages.

# Hence V4 introduces a bounded harvesting policy:

# 1. Root packages are always fully included.
# 2. Only a small number of immediate transitive dependencies are retained.
# 3. Optional/test/extras dependency noise is aggressively discarded.

# This keeps the experiment:
# - reproducible,
# - bounded,
# - interpretable,
# - conference-demonstrable.

# GROUNDING TO PROPOSAL
# ---------------------
# The proposal explicitly promises:
# 'controlled number of projects'
# 'offline analytical experimentation'
# 'prototype-level implementation'

# Therefore unlimited dependency closure would violate methodological validity.
# """

# import requests
# import re
# from datetime import datetime, timezone
# from typing import Dict, List, Set
# from .models import PackageNode
# from .config import *

# # V4 bounded contextual expansion:
# MAX_CHILDREN_PER_ROOT = 3


# def extract_dependencies(requirements_path: str) -> List[str]:
#     """
#     Read analyst-supplied root dependency manifest.

#     WHY:
#     IDRF begins from human-selected projects/packages, not internet-wide package crawling.
#     """
#     deps = []
#     with open(requirements_path, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if line and not line.startswith("#"):
#                 pkg = re.split(r'[<>=!~]', line)[0].strip()
#                 if pkg:
#                     deps.append(pkg.lower())
#     return deps


# def clean_dep_name(dep_string: str) -> str:
#     """
#     Clean PyPI requires_dist strings into package names.

#     WHY:
#     PyPI metadata often contains:
#     package_name (>=x); python_version<...
#     We only need canonical package token for bounded structural modeling.
#     """
#     dep_string = dep_string.split(";")[0]
#     dep_string = dep_string.split("(")[0]
#     return dep_string.strip().lower()


# def safe_get(url: str):
#     """
#     Network-safe HTTP fetch with timeout.

#     WHY:
#     Conference prototype must not hang indefinitely during ETL.
#     """
#     try:
#         return requests.get(url, timeout=REQUEST_TIMEOUT)
#     except:
#         return None


# def fetch_pypi_metadata(package_name: str) -> dict:
#     """
#     Fetch public PyPI metadata for a package.

#     Returns:
#     - requires_dist
#     - project_urls
#     """
#     url = f"https://pypi.org/pypi/{package_name}/json"
#     r = safe_get(url)
#     if r and r.status_code == 200:
#         info = r.json()["info"]
#         return {
#             "requires_dist": info.get("requires_dist") or [],
#             "project_urls": info.get("project_urls") or {}
#         }
#     return {"requires_dist": [], "project_urls": {}}


# def extract_github_repo(project_urls: dict):
#     """
#     Attempt to recover GitHub repository URL from PyPI project URLs.

#     WHY:
#     GitHub public metadata provides a lightweight maintainability proxy.
#     """
#     for _, url in project_urls.items():
#         if "github.com" in url.lower():
#             match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
#             if match:
#                 owner = match.group(1)
#                 repo = match.group(2).replace(".git", "")
#                 return f"{owner}/{repo}"
#     return None


# def fetch_github_metadata(repo_slug: str):
#     """
#     Fetch stars and last update from GitHub.

#     FALLBACK:
#     If unavailable, conservative bounded defaults are used.
#     """
#     if not repo_slug:
#         return 10, 365

#     r = safe_get(GITHUB_API + repo_slug)
#     if r and r.status_code == 200:
#         data = r.json()
#         stars = data.get("stargazers_count", 10)
#         pushed = data.get("pushed_at")
#         if pushed:
#             dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#             days = (datetime.now(timezone.utc) - dt).days
#         else:
#             days = 365
#         return stars, days

#     return 10, 365


# def build_package_nodes(requirements_path: str) -> Dict[str, PackageNode]:
#     """
#     Build bounded package node universe.

#     V4 DESIGN CHANGE:
#     -----------------
#     Previous versions recursively harvested the full transitive closure,
#     causing hundreds of irrelevant packages and cognitive overload.

#     V4 intentionally keeps:
#     - all root packages
#     - only first MAX_CHILDREN_PER_ROOT cleaned transitive children per root

#     This preserves structural context without destroying interpretability.
#     """
#     root_packages = extract_dependencies(requirements_path)
#     nodes: Dict[str, PackageNode] = {}
#     visited: Set[str] = set()

#     for root in root_packages:
#         if root in visited:
#             continue

#         visited.add(root)

#         meta = fetch_pypi_metadata(root)
#         repo = extract_github_repo(meta["project_urls"])
#         stars, last_update_days = fetch_github_metadata(repo)

#         child_names = []
#         for dep in meta["requires_dist"]:
#             cname = clean_dep_name(dep)
#             if cname and cname != root:
#                 child_names.append(cname)

#         child_names = child_names[:MAX_CHILDREN_PER_ROOT]

#         nodes[root] = PackageNode(
#             name=root,
#             direct_dependencies=child_names,
#             maintainer_count=1,
#             stars=stars,
#             last_update_days=last_update_days
#         )

#         for child in child_names:
#             if child in visited:
#                 continue

#             visited.add(child)

#             cmeta = fetch_pypi_metadata(child)
#             crepo = extract_github_repo(cmeta["project_urls"])
#             cstars, cdays = fetch_github_metadata(crepo)

#             nodes[child] = PackageNode(
#                 name=child,
#                 direct_dependencies=[],
#                 maintainer_count=1,
#                 stars=cstars,
#                 last_update_days=cdays
#             )

#     return nodes






# """
# IDRF Data Processing Module (V4.1 Conference-Stable Prototype)
# --------------------------------------------------------------

# GROUNDING
# ---------
# Implements:
# - Proposal Section 5.1 Data Source and Scope
# - GitHub Issues #3, #14, #15

# V4.1 DESIGN PHILOSOPHY
# ----------------------
# The framework should not explode into internet-scale crawling, but it must also
# not create analytically empty placeholder children.

# Therefore this version performs:

# 1. full metadata enrichment for root packages,
# 2. bounded first-level transitive contextual expansion,
# 3. bounded second-level child linkage storage (without infinite recursion).

# This preserves:
# - interpretability,
# - stable runtime,
# - richer structural validity.
# """

# import requests
# import re
# from datetime import datetime, timezone
# from typing import Dict, List, Set
# from .models import PackageNode
# from .config import *

# MAX_CHILDREN_PER_ROOT = 6
# MAX_CHILDREN_PER_TRANSITIVE = 2


# def safe_get(url: str):
#     """Bounded timeout HTTP getter for reproducible ETL."""
#     try:
#         return requests.get(url, timeout=REQUEST_TIMEOUT)
#     except:
#         return None


# def normalize_package_name(raw: str) -> str:
#     """
#     Canonicalize package strings from requirements.txt or requires_dist.

#     WHY:
#     PyPI dependency strings may contain:
#     - version operators
#     - extras
#     - commas
#     - markers
#     - spaces

#     Only canonical package token should enter graph modeling.
#     """
#     raw = raw.split(";")[0]
#     raw = raw.split("[")[0]
#     raw = raw.split("(")[0]
#     raw = raw.split(",")[0]
#     raw = re.split(r"[<>=!~ ]+", raw)[0]
#     return raw.strip().lower()


# def extract_dependencies(requirements_path: str) -> List[str]:
#     """
#     Read analyst-controlled root dependencies.

#     Implements GitHub issue #14.
#     """
#     deps = []
#     with open(requirements_path, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if line and not line.startswith("#"):
#                 pkg = normalize_package_name(line)
#                 if pkg:
#                     deps.append(pkg)
#     return deps


# def fetch_pypi_metadata(package_name: str) -> dict:
#     """
#     Fetch bounded PyPI metadata.

#     Returns:
#     - requires_dist
#     - project_urls
#     - maintainer_count proxy
#     """
#     r = safe_get(f"https://pypi.org/pypi/{package_name}/json")
#     if r and r.status_code == 200:
#         info = r.json().get("info", {})
#         reqs = info.get("requires_dist") or []
#         reqs = [normalize_package_name(x) for x in reqs if normalize_package_name(x)]

#         maintainer_proxy = 1 if info.get("author") else 2

#         return {
#             "requires_dist": reqs,
#             "project_urls": info.get("project_urls") or {},
#             "maintainer_count": maintainer_proxy
#         }

#     return {
#         "requires_dist": [],
#         "project_urls": {},
#         "maintainer_count": 2
#     }


# def extract_github_repo(project_urls: dict):
#     """Recover GitHub owner/repo slug when publicly available."""
#     for _, url in project_urls.items():
#         if "github.com" in url.lower():
#             m = re.search(r"github\.com/([^/]+)/([^/]+)", url)
#             if m:
#                 return f"{m.group(1)}/{m.group(2).replace('.git','')}"
#     return None


# def fetch_github_metadata(repo_slug: str):
#     """
#     Fetch bounded repository vitality metadata.

#     Returns:
#     stars, last_update_days
#     """
#     if not repo_slug:
#         return 10, 365

#     r = safe_get(GITHUB_API + repo_slug)
#     if r and r.status_code == 200:
#         d = r.json()
#         stars = d.get("stargazers_count", 10)

#         pushed = d.get("pushed_at")
#         if pushed:
#             dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#             days = (datetime.now(timezone.utc) - dt).days
#         else:
#             days = 365

#         return stars, days

#     return 10, 365


# def build_package_nodes(requirements_path: str) -> Dict[str, PackageNode]:
#     """
#     Build bounded enriched dependency universe.

#     Implements GitHub issue #15 in a conference-safe bounded manner:
#     root -> enriched direct children -> shallow contextual grandchildren list.
#     """
#     root_packages = extract_dependencies(requirements_path)
#     nodes: Dict[str, PackageNode] = {}
#     visited: Set[str] = set()

#     for root in root_packages:
#         if root in visited:
#             continue
#         visited.add(root)

#         root_meta = fetch_pypi_metadata(root)
#         root_repo = extract_github_repo(root_meta["project_urls"])
#         root_stars, root_days = fetch_github_metadata(root_repo)

#         root_children = root_meta["requires_dist"][:MAX_CHILDREN_PER_ROOT]

#         nodes[root] = PackageNode(
#             name=root,
#             direct_dependencies=root_children,
#             maintainer_count=root_meta["maintainer_count"],
#             stars=root_stars,
#             last_update_days=root_days
#         )

#         for child in root_children:
#             if child in visited:
#                 continue
#             visited.add(child)

#             child_meta = fetch_pypi_metadata(child)
#             child_repo = extract_github_repo(child_meta["project_urls"])
#             child_stars, child_days = fetch_github_metadata(child_repo)

#             shallow_children = child_meta["requires_dist"][:MAX_CHILDREN_PER_TRANSITIVE]

#             nodes[child] = PackageNode(
#                 name=child,
#                 direct_dependencies=shallow_children,
#                 maintainer_count=child_meta["maintainer_count"],
#                 stars=child_stars,
#                 last_update_days=child_days
#             )

#     return nodes








"""
IDRF Data Processing Module (V5 Research-Stable Conference Prototype)
---------------------------------------------------------------------

Grounded in:
- Proposal Section 5.1 Data Source and Scope
- GitHub Issues #3, #14, #15

V5 DESIGN DECISION
------------------
IDRF is a human-centered analytical reasoning framework, not a full internet
dependency crawler.

Therefore V5 intentionally models:

ROOT PACKAGE + MEANINGFUL FIRST-LEVEL RUNTIME CONTEXT

and aggressively removes:
- optional extras,
- testing dependencies,
- documentation dependencies,
- platform-only auxiliary packages.

This preserves structural interpretability and avoids graph pollution.
"""

import requests
import re
from datetime import datetime, timezone
from typing import Dict, List, Set
from .models import PackageNode
from .config import *

MAX_CHILDREN_PER_ROOT = 6

NOISE_KEYWORDS = [
    "test", "tests", "testing", "pytest",
    "doc", "docs", "sphinx",
    "dev", "lint", "tox",
    "colorama", "babel", "zipp"
]


def safe_get(url: str):
    try:
        return requests.get(url, timeout=REQUEST_TIMEOUT)
    except:
        return None


def normalize_package_name(raw: str) -> str:
    raw = raw.split(";")[0]
    raw = raw.split("[")[0]
    raw = raw.split("(")[0]
    raw = raw.split(",")[0]
    raw = re.split(r"[<>=!~ ]+", raw)[0]
    return raw.strip().lower()


def is_meaningful_runtime_dep(dep_raw: str) -> bool:
    """
    Remove optional/test/doc/platform noise from PyPI metadata.
    """
    low = dep_raw.lower()

    if "extra ==" in low:
        return False

    if any(k in low for k in NOISE_KEYWORDS):
        return False

    name = normalize_package_name(dep_raw)
    if not name:
        return False

    return True


def extract_dependencies(requirements_path: str) -> List[str]:
    deps = []
    with open(requirements_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pkg = normalize_package_name(line)
                if pkg:
                    deps.append(pkg)
    return deps


def fetch_pypi_metadata(package_name: str) -> dict:
    r = safe_get(f"https://pypi.org/pypi/{package_name}/json")
    if r and r.status_code == 200:
        info = r.json().get("info", {})
        raw_reqs = info.get("requires_dist") or []

        reqs = [
            normalize_package_name(x)
            for x in raw_reqs
            if is_meaningful_runtime_dep(x)
        ]

        maintainer_proxy = 1 if info.get("author") else 2

        return {
            "requires_dist": reqs,
            "project_urls": info.get("project_urls") or {},
            "maintainer_count": maintainer_proxy
        }

    return {
        "requires_dist": [],
        "project_urls": {},
        "maintainer_count": 2
    }


def extract_github_repo(project_urls: dict):
    for _, url in project_urls.items():
        if "github.com" in url.lower():
            m = re.search(r"github\.com/([^/]+)/([^/]+)", url)
            if m:
                return f"{m.group(1)}/{m.group(2).replace('.git','')}"
    return None


def fetch_github_metadata(repo_slug: str):
    if not repo_slug:
        return 10, 365

    r = safe_get(GITHUB_API + repo_slug)
    if r and r.status_code == 200:
        d = r.json()
        stars = d.get("stargazers_count", 10)

        pushed = d.get("pushed_at")
        if pushed:
            dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            days = (datetime.now(timezone.utc) - dt).days
        else:
            days = 365

        return stars, days

    return 10, 365


def build_package_nodes(requirements_path: str) -> Dict[str, PackageNode]:
    """
    V5 bounded package universe:
    root + filtered first-level contextual children only.
    """
    root_packages = extract_dependencies(requirements_path)
    nodes: Dict[str, PackageNode] = {}
    visited: Set[str] = set()

    for root in root_packages:
        if root in visited:
            continue
        visited.add(root)

        root_meta = fetch_pypi_metadata(root)
        root_repo = extract_github_repo(root_meta["project_urls"])
        root_stars, root_days = fetch_github_metadata(root_repo)

        root_children = root_meta["requires_dist"][:MAX_CHILDREN_PER_ROOT]

        nodes[root] = PackageNode(
            name=root,
            direct_dependencies=root_children,
            maintainer_count=root_meta["maintainer_count"],
            stars=root_stars,
            last_update_days=root_days
        )

        # for child in root_children:
        #     if child in visited:
        #         continue
        #     visited.add(child)

        #     child_meta = fetch_pypi_metadata(child)
        #     child_repo = extract_github_repo(child_meta["project_urls"])
        #     child_stars, child_days = fetch_github_metadata(child_repo)

        #     nodes[child] = PackageNode(
        #         name=child,
        #         direct_dependencies=[],
        #         maintainer_count=child_meta["maintainer_count"],
        #         stars=child_stars,
        #         last_update_days=child_days
        #     )
        for child in root_children:
            if child in visited:
                continue
            visited.add(child)

            child_meta = fetch_pypi_metadata(child)
            child_repo = extract_github_repo(child_meta["project_urls"])
            child_stars, child_days = fetch_github_metadata(child_repo)

            shallow_children = child_meta["requires_dist"][:2]

            nodes[child] = PackageNode(
                name=child,
                direct_dependencies=shallow_children,
                maintainer_count=child_meta["maintainer_count"],
                stars=child_stars,
                last_update_days=child_days
            )

            # ---- bounded grandchild materialization (MANDATORY) ----
            for grand in shallow_children:
                if grand in visited:
                    continue

                visited.add(grand)

                gmeta = fetch_pypi_metadata(grand)
                grepo = extract_github_repo(gmeta["project_urls"])
                gstars, gdays = fetch_github_metadata(grepo)

                nodes[grand] = PackageNode(
                    name=grand,
                    direct_dependencies=[],
                    maintainer_count=gmeta["maintainer_count"],
                    stars=gstars,
                    last_update_days=gdays
                )            

    return nodes    