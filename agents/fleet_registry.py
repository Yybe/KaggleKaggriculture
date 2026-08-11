"""Canonical test fleet for Kaggriculture agent benchmarking.

Persists the 8 BEHAVIORALLY DISTINCT local model groups (discovered via
champion-interaction signature dedup of the 12-model fleet) plus the current
champion (V18 APEXX) and the canonical fresh-seed test set.

WHY: The full agents/ directory contains many files that are ALIASES of each
other (loaded bases / identical champion-interaction fingerprints). Benchmarks
that include aliases waste runtime and distort comparisons. This registry is
the single source of truth for "who are the real distinct opponents".

ALIAS MAP (non-canonical file -> canonical distinct group):
  kaggle_v26b                    -> v23_kaito      (kaggle_v26b.py loads kaggle_v23.py as its base)
  kaggle_boat84_v14              -> salemali7_3k
  kaggle_champion_v155           -> v17_apex
  kaggle_v16a_counterpreempt     -> v17_apex

USAGE (see tools/benchmark_agent_fleet.py):
  Any candidate agent is benchmarked against the 8 distinct groups PLUS the
  current champion (9 fixed opponents) on the canonical FRESH_SEEDS set.
"""
import importlib
import os
import sys

# Make repo root importable regardless of CWD.
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

# ---------------------------------------------------------------------------
# Canonical FRESH seed set - deliberately disjoint from the original 8 gate
# seeds ([1000000, 2000000, 3330000, 5000000, 6000000, 7770000, 8000000,
# 9000000]). V18 APEXX won 432/432 on this set in rebench_fresh_v18apexx.
# ---------------------------------------------------------------------------
FRESH_SEEDS = [
    314159, 2718281, 1414213, 1732050, 2236067, 2645751,
    3162277, 3245553, 3316624, 3464101, 3588989, 3660254,
    2426406, 2469507, 2549509, 2641391, 2745995, 2871778,
]

# ---------------------------------------------------------------------------
# Champion - V18 APEXX (the tuned submission). Stateful -> fresh instance per
# match via fresh_cls.
# ---------------------------------------------------------------------------
CHAMPION_SPEC = {
    "label": "v18_apexx",
    "module": "agents.kaggle_v18_apexx",
    "attr": "agent",
    "fresh_cls": "V18ApexAgent",
    "file": "agents/kaggle_v18_apexx.py",
    "aliases": [],
    "notes": "Holds seeds 1 & 2 = THUNDER clones (self-play heat / near-border)",
}

# ---------------------------------------------------------------------------
# The 8 distinct behavior groups (canonical member + provenance).
# ---------------------------------------------------------------------------
DISTINCT_FLEET = {
    "v14_tweaked": {
        "label": "v14_tweaked",
        "module": "agents.kaggle_v14_tweaked",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/kaggle_v14_tweaked.py",
        "aliases": [],
        "notes": "Tweaked (augmented) variant on the older V14 line",
    },
    "v22_romanrozen": {
        "label": "v22_romanrozen",
        "module": "agents.kaggle_v22_romanrozen",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/kaggle_v22_romanrozen.py",
        "aliases": [],
        "notes": "Community route variant (romanrozen)",
    },
    "v26_aggr": {
        "label": "v26_aggr",
        "module": "agents.kaggle_v26_aggr_evidence",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/kaggle_v26_aggr_evidence.py",
        "aliases": [],
        "notes": "Aggressive evidence variant - strongest opponent vs V18 APEXX",
    },
    "champ_v15": {
        "label": "champ_v15",
        "module": "agents.kaggle_champion_v15",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/kaggle_champion_v15.py",
        "aliases": [],
        "notes": "V15 champion line (pre-V16a)",
    },
    "v23_kaito": {
        "label": "v23_kaito",
        "module": "agents.kaggle_v23",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/kaggle_v23.py",
        "aliases": ["v26b"],
        "notes": "kaggle_v26b.py loads kaggle_v23.py as its base (literal alias)",
    },
    "v14_v26style": {
        "label": "v14_v26style",
        "module": "agents.kaggle_v14_v26style",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/kaggle_v14_v26style.py",
        "aliases": [],
        "notes": "V14 base driven in the v26 style",
    },
    "salemali7_3k": {
        "label": "salemali7_3k",
        "module": "agents.salemali7_3000score",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/salemali7_3000score.py",
        "aliases": ["boat84_v14"],
        "notes": "aka boat84_v14 (identical champion-interaction fingerprint)",
    },
    "v17_apex": {
        "label": "v17_apex",
        "module": "agents.submission_v16a_backup_20260810",
        "attr": "agent",
        "fresh_cls": None,
        "file": "agents/submission_v16a_backup_20260810.py",
        "aliases": ["v155_champion", "v16a_counter"],
        "notes": "Previous champion (Apex Counter-Relay). v155/v16a are behavior aliases.",
    },
}

# ---------------------------------------------------------------------------
# Full opponent set for benchmarking a candidate: 8 distinct + current champion.
# Excludes the champion from its own opponents (see benchmark_agent_fleet.py).
# ---------------------------------------------------------------------------
def _fleet(v18_included=True):
    f = dict(DISTINCT_FLEET)
    if v18_included:
        f[CHAMPION_SPEC["label"]] = dict(CHAMPION_SPEC)
    return f


# Default: candidate fought vs 8 distinct + champion (9 opponents).
FLEET = _fleet(v18_included=True)

# Map alias/source filename -> canonical label (informational).
ALIAS_TO_CANONICAL = {}
for _label, _spec in DISTINCT_FLEET.items():
    for _alias in _spec.get("aliases", []):
        ALIAS_TO_CANONICAL[_alias] = _label


def load_callable(spec, fresh_instance=True):
    """Resolve a spec to a callable agent.

    Stateful agents (fresh_cls set) return a NEW instance per call when
    fresh_instance=True, so each match gets a clean state carrier.
    """
    module = importlib.import_module(spec["module"])
    if spec.get("fresh_cls"):
        cls = getattr(module, spec["fresh_cls"])
        return cls() if fresh_instance else getattr(module, spec.get("attr", "agent"))
    return getattr(module, spec.get("attr", "agent"))


def canonical_label(name):
    """Map any known alias/file-label back to its canonical distinct group."""
    return ALIAS_TO_CANONICAL.get(name)
