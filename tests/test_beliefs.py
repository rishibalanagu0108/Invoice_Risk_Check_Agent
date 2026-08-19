import json
from pathlib import Path

import pytest

from invoice_agent.beliefs import (
    calculate_beliefs,
    calculate_prior,
    load_assumptions,
    normalize_probabilities,
)
from invoice_agent.models import HiddenState


CONFIG_PATH = Path(__file__).parents[1] / "config" / "simulation_assumptions.json"


@pytest.fixture()
def config() -> dict:
    return load_assumptions(CONFIG_PATH)


def test_prior_is_normalized(config: dict) -> None:
    beliefs = calculate_prior(config)

    assert sum(beliefs.values()) == pytest.approx(1.0)
    assert set(beliefs) == set(HiddenState)


def test_beliefs_are_normalized_after_evidence(config: dict) -> None:
    beliefs = calculate_beliefs(
        {"bank_account_changed": True, "unusual_urgency": True}, config
    )

    assert sum(beliefs.values()) == pytest.approx(1.0)
    assert all(0 <= value <= 1 for value in beliefs.values())


def test_risk_signals_increase_fraud_belief(config: dict) -> None:
    safe = calculate_beliefs(
        {"bank_account_changed": False, "unusual_urgency": False}, config
    )
    risky = calculate_beliefs(
        {"bank_account_changed": True, "unusual_urgency": True}, config
    )

    assert risky[HiddenState.FRAUD] > safe[HiddenState.FRAUD]


def test_unconfigured_evidence_does_not_change_prior(config: dict) -> None:
    prior = calculate_prior(config)
    beliefs = calculate_beliefs({"invoice_amount": 5000}, config)

    assert beliefs == prior


def test_zero_scores_are_rejected() -> None:
    with pytest.raises(ValueError, match="positive total"):
        normalize_probabilities({state: 0 for state in HiddenState})
