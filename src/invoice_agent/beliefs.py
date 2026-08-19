"""Simple, configurable Bayesian-style belief updates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .models import HiddenState

Beliefs = dict[HiddenState, float]


def load_assumptions(path: str | Path) -> dict[str, Any]:
    """Load priors and likelihood assumptions from a JSON file."""

    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def _state_key(state: HiddenState | str) -> str:
    return state.value if isinstance(state, HiddenState) else state


def normalize_probabilities(values: Mapping[HiddenState | str, float]) -> Beliefs:
    """Normalize non-negative state scores so they sum to one."""

    scores = {
        HiddenState(state): float(values[_state_key(state)])
        for state in HiddenState
    }
    if any(score < 0 for score in scores.values()):
        raise ValueError("probability scores must be non-negative")
    total = sum(scores.values())
    if total <= 0:
        raise ValueError("probability scores must have a positive total")
    return {state: score / total for state, score in scores.items()}


def calculate_prior(config: Mapping[str, Any]) -> Beliefs:
    """Return the normalized prior distribution from configuration."""

    return normalize_probabilities(config["priors"])


def _observed_key(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def incorporate_observed_evidence(
    prior: Mapping[HiddenState | str, float],
    evidence: Mapping[str, Any],
    likelihoods: Mapping[str, Any],
) -> Beliefs:
    """Update beliefs using configured likelihoods for observed evidence.

    Features without a configured likelihood are ignored intentionally. This
    lets the case schema grow without silently inventing model behavior.
    """

    scores = {
        state: probability for state, probability in normalize_probabilities(prior).items()
    }
    for feature, feature_likelihoods in likelihoods.items():
        if feature not in evidence:
            continue
        observed = _observed_key(evidence[feature])
        if observed not in feature_likelihoods:
            raise ValueError(f"no likelihood configured for {feature}={observed}")
        for state in HiddenState:
            likelihood = float(feature_likelihoods[observed][_state_key(state)])
            if likelihood < 0:
                raise ValueError("likelihoods must be non-negative")
            scores[state] *= likelihood
    return normalize_probabilities(scores)


def calculate_beliefs(
    evidence: Mapping[str, Any], config: Mapping[str, Any]
) -> Beliefs:
    """Calculate posterior beliefs from evidence and configuration."""

    prior = calculate_prior(config)
    return incorporate_observed_evidence(
        prior, evidence, config.get("likelihoods", {})
    )
