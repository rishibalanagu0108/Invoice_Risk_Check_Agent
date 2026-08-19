from pathlib import Path

import pytest

from invoice_agent.beliefs import load_assumptions
from invoice_agent.models import Action, HiddenState, InvoiceCase
from invoice_agent.policies import (
    baseline_action,
    expected_costs,
    policy_a_action,
    policy_b_action,
)


CONFIG_PATH = Path(__file__).parents[1] / "config" / "simulation_assumptions.json"


@pytest.fixture()
def config() -> dict:
    return load_assumptions(CONFIG_PATH)


def make_case(**overrides: object) -> InvoiceCase:
    values: dict[str, object] = {
        "case_id": "case-001",
        "vendor_id": "vendor-001",
        "vendor_age_days": 800,
        "existing_vendor": True,
        "invoice_amount": 1000.0,
        "historical_average_amount": 900.0,
        "bank_account_changed": False,
        "bank_change_age_days": None,
        "email_domain_changed": False,
        "lookalike_domain_signal": False,
        "invoice_number_pattern_valid": True,
        "duplicate_invoice_signal": False,
        "purchase_order_match": True,
        "payment_terms_match": True,
        "unusual_urgency": False,
        "location_changed": False,
        "vendor_contact_verified": True,
        "callback_verified": None,
        "supporting_documents_available": True,
    }
    values.update(overrides)
    return InvoiceCase(**values)  # type: ignore[arg-type]


def test_expected_costs_use_beliefs_and_costs(config: dict) -> None:
    beliefs = {
        HiddenState.LEGITIMATE: 0.7,
        HiddenState.ERROR: 0.2,
        HiddenState.FRAUD: 0.1,
    }

    costs = expected_costs(beliefs, config["costs"])

    assert costs[Action.APPROVE] == pytest.approx(15.0)
    assert costs[Action.VERIFY] == pytest.approx(6.1)


def test_baseline_rule_order(config: dict) -> None:
    assert baseline_action(make_case(duplicate_invoice_signal=True)) == Action.HOLD
    assert baseline_action(make_case(bank_account_changed=True)) == Action.VERIFY
    assert baseline_action(make_case(unusual_urgency=True)) == Action.ESCALATE
    assert baseline_action(make_case()) == Action.APPROVE


def test_risk_sensitive_policy_verifies_earlier(config: dict) -> None:
    beliefs = {
        HiddenState.LEGITIMATE: 0.65,
        HiddenState.ERROR: 0.1,
        HiddenState.FRAUD: 0.25,
    }

    assert policy_a_action(beliefs, config) == Action.APPROVE
    assert policy_b_action(beliefs, config) == Action.VERIFY


def test_high_fraud_probability_requires_escalation_or_hold(config: dict) -> None:
    beliefs = {
        HiddenState.LEGITIMATE: 0.05,
        HiddenState.ERROR: 0.05,
        HiddenState.FRAUD: 0.9,
    }

    assert policy_a_action(beliefs, config) in {Action.HOLD, Action.ESCALATE}
    assert policy_b_action(beliefs, config) in {Action.HOLD, Action.ESCALATE}
