"""Cost-sensitive policies and the simple rule-based baseline."""

from __future__ import annotations

from typing import Any, Mapping

from .beliefs import Beliefs
from .models import Action, HiddenState, InvoiceCase


def expected_costs(
    beliefs: Beliefs, costs: Mapping[str, Mapping[str, float]]
) -> dict[Action, float]:
    """Calculate probability-weighted cost for every available action."""

    return {
        action: sum(
            beliefs[state] * float(costs[action.value][state.value])
            for state in HiddenState
        )
        for action in Action
    }


def lowest_cost_action(
    beliefs: Beliefs,
    costs: Mapping[str, Mapping[str, float]],
    allowed_actions: tuple[Action, ...] = tuple(Action),
) -> Action:
    """Return the lowest expected-cost action with deterministic tie-breaking."""

    calculated = expected_costs(beliefs, costs)
    return min(allowed_actions, key=lambda action: (calculated[action], action.value))


def baseline_action(case: InvoiceCase) -> Action:
    """Apply the deliberately simple rule-based baseline."""

    if case.duplicate_invoice_signal:
        return Action.HOLD
    if case.bank_account_changed:
        return Action.VERIFY
    if case.lookalike_domain_signal or case.unusual_urgency:
        return Action.ESCALATE
    return Action.APPROVE


def _policy_thresholds(
    config: Mapping[str, Any], policy_name: str
) -> Mapping[str, float]:
    try:
        return config["policies"][policy_name]
    except KeyError as error:
        raise ValueError(f"unknown policy: {policy_name}") from error


def policy_action(
    beliefs: Beliefs,
    config: Mapping[str, Any],
    policy_name: str,
    evidence: Mapping[str, Any] | None = None,
) -> Action:
    """Choose an action using fraud thresholds and expected costs.

    Lower thresholds make a policy more cautious. Thresholds gate approval and
    escalation; expected costs choose among the remaining actions in a risk
    band.
    """

    thresholds = _policy_thresholds(config, policy_name)
    fraud_probability = beliefs[HiddenState.FRAUD]
    costs = config["costs"]

    # Safety gate: direct approval is not allowed when the evidence contains
    # an explicit duplicate or multiple simultaneous high-risk signals.
    if evidence and (
        evidence.get("duplicate_invoice_signal")
        or evidence.get("multiple_high_risk_signals")
    ):
        return lowest_cost_action(
            beliefs, costs, (Action.VERIFY, Action.HOLD, Action.ESCALATE)
        )

    if fraud_probability >= thresholds["escalate_fraud_probability"]:
        allowed = (Action.HOLD, Action.ESCALATE)
    elif fraud_probability >= thresholds["hold_fraud_probability"]:
        allowed = (Action.VERIFY, Action.HOLD, Action.ESCALATE)
    elif fraud_probability >= thresholds["verify_fraud_probability"]:
        allowed = (Action.VERIFY, Action.HOLD, Action.ESCALATE)
    else:
        return Action.APPROVE

    return lowest_cost_action(beliefs, costs, allowed)


def policy_a_action(
    beliefs: Beliefs,
    config: Mapping[str, Any],
    evidence: Mapping[str, Any] | None = None,
) -> Action:
    """Efficiency-oriented policy with higher risk thresholds."""

    return policy_action(beliefs, config, "efficiency", evidence)


def policy_b_action(
    beliefs: Beliefs,
    config: Mapping[str, Any],
    evidence: Mapping[str, Any] | None = None,
) -> Action:
    """Risk-sensitive policy with lower risk thresholds."""

    return policy_action(beliefs, config, "risk_sensitive", evidence)
