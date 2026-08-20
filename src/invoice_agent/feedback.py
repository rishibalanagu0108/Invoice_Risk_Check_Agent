"""Simulated verification feedback and second decisions."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from .beliefs import calculate_beliefs, load_assumptions
from .data_generation import load_cases_csv
from .models import Action, HiddenState, InvoiceCase
from .policies import baseline_action, policy_a_action, policy_b_action


def apply_callback_result(case: InvoiceCase, callback_verified: bool) -> InvoiceCase:
    """Return a copy containing verification evidence.

    A successful verification resolves a suspected duplicate signal in the
    simulation. This models an accounting check that confirms the invoice is
    not actually a duplicate.
    """

    return replace(
        case,
        callback_verified=callback_verified,
        duplicate_invoice_signal=(
            False if callback_verified and case.duplicate_invoice_signal
            else case.duplicate_invoice_signal
        ),
    )


def simulate_callback_result(case: InvoiceCase) -> bool:
    """Simulate a callback outcome using the evaluator-only hidden label.

    This is an experimental oracle, not a real verification service. The agent
    receives only the returned boolean after its initial VERIFY action.
    """

    return case.true_state is HiddenState.LEGITIMATE


def _decide(
    case: InvoiceCase, config: Mapping[str, Any], policy: str
) -> dict[str, Any]:
    evidence = case.observation()
    beliefs = calculate_beliefs(evidence, config)
    if policy == "baseline":
        action = baseline_action(case)
    elif policy == "policy_a":
        action = policy_a_action(beliefs, config, evidence)
    elif policy == "policy_b":
        action = policy_b_action(beliefs, config, evidence)
    else:
        raise ValueError(f"unknown policy: {policy}")
    return {
        "evidence": evidence,
        "beliefs": {state.value: value for state, value in beliefs.items()},
        "action": action.value,
    }


def run_feedback_experiment(
    cases_path: str | Path = "data/cases.csv",
    config_path: str | Path = "config/simulation_assumptions.json",
    output_path: str | Path = "results/feedback_results.json",
) -> list[dict[str, Any]]:
    """Run initial and post-callback decisions for cases initially verified."""

    cases = load_cases_csv(cases_path)
    config = load_assumptions(config_path)
    records: list[dict[str, Any]] = []

    for case in cases:
        for policy in ("baseline", "policy_a", "policy_b"):
            initial = _decide(case, config, policy)
            if initial["action"] != Action.VERIFY.value:
                continue
            callback_verified = simulate_callback_result(case)
            updated_case = apply_callback_result(case, callback_verified)
            post_feedback = _decide(updated_case, config, policy)
            records.append(
                {
                    "case_id": case.case_id,
                    "policy": policy,
                    "true_state": case.true_state.value,
                    "initial": initial,
                    "new_evidence": {"callback_verified": callback_verified},
                    "post_feedback": post_feedback,
                }
            )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)
        file.write("\n")
    return records
