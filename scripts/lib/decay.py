"""Decay-state classification — implements references/decay-model.md.

Pure function of dates and thresholds; no I/O, no model calls, no
side effects. Used by the index generator (scripts/lib/index_generator.py).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

CONFIRMED_RE = re.compile(r"\[confirmed:(\d{4}-\d{2}-\d{2})\]")

DEFAULT_THRESHOLD_FRESH = 60
DEFAULT_THRESHOLD_DORMANT = 180
DEFAULT_THRESHOLD_COLD = 365

TYPE_MODIFIERS = {
    "GOTCHA": 1.5,
    "RECIPE": 1.5,
    "CORRECTION": float("inf"),  # never decays
}

PROFILE_MULTIPLIERS = {"fast": 0.5, "normal": 1.0, "slow": 2.0}

STATES = ("Fresh", "Stale", "Dormant", "Cold")


@dataclass(frozen=True)
class DecayThresholds:
    fresh: float = DEFAULT_THRESHOLD_FRESH
    dormant: float = DEFAULT_THRESHOLD_DORMANT
    cold: float = DEFAULT_THRESHOLD_COLD


def parse_decay_config(text: str) -> DecayThresholds:
    """Parse a `.decay-config.md`-shaped file for the three thresholds.

    Tolerant of missing/malformed values — falls back to documented
    defaults for anything not found.
    """

    def _find(key: str, default: float) -> float:
        match = re.search(rf"^{key}:\s*(\d+)", text, re.MULTILINE)
        return float(match.group(1)) if match else default

    return DecayThresholds(
        fresh=_find("threshold_fresh", DEFAULT_THRESHOLD_FRESH),
        dormant=_find("threshold_dormant", DEFAULT_THRESHOLD_DORMANT),
        cold=_find("threshold_cold", DEFAULT_THRESHOLD_COLD),
    )


def extract_confirmed_dates(text: str) -> list[date]:
    dates = []
    for m in CONFIRMED_RE.finditer(text):
        try:
            dates.append(datetime.strptime(m.group(1), "%Y-%m-%d").date())
        except ValueError:
            continue
    return dates


def extract_decay_profile(text: str) -> str:
    match = re.search(r"^decay_profile:\s*(fast|normal|slow)\s*$", text, re.MULTILINE)
    return match.group(1) if match else "normal"


def extract_entry_types(text: str) -> set[str]:
    return set(re.findall(r"^\[[^\]]+\]\s+(INSIGHT|LESSON|MODEL|GOTCHA|RECIPE|CORRECTION|DECISION)\b", text, re.MULTILINE))


def classify(
    *,
    last_confirmed: date | None,
    today: date,
    thresholds: DecayThresholds = DecayThresholds(),
    entry_types: frozenset[str] = frozenset(),
    decay_profile: str = "normal",
) -> str:
    """Return one of Fresh / Stale / Dormant / Cold.

    `last_confirmed=None` (no [confirmed:...] tag found at all) is treated
    by the caller falling back to file mtime before calling this — this
    function always requires a concrete date to classify against.
    """
    if last_confirmed is None:
        return "Cold"

    days_since = (today - last_confirmed).days
    if days_since < 0:
        days_since = 0

    type_modifier = 1.0
    for t in entry_types:
        modifier = TYPE_MODIFIERS.get(t, 1.0)
        if modifier == float("inf"):
            return "Fresh"  # CORRECTION never decays
        type_modifier = max(type_modifier, modifier)

    profile_multiplier = PROFILE_MULTIPLIERS.get(decay_profile, 1.0)

    effective_fresh = thresholds.fresh * type_modifier * profile_multiplier
    effective_dormant = thresholds.dormant * type_modifier * profile_multiplier
    effective_cold = thresholds.cold * type_modifier * profile_multiplier

    if days_since <= effective_fresh:
        return "Fresh"
    if days_since <= effective_dormant:
        return "Stale"
    if days_since <= effective_cold:
        return "Dormant"
    return "Cold"
