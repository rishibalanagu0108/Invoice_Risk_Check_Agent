"""Reproducible experiment runner for the three decision systems."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from .beliefs import calculate_beliefs, load_assumptions
from .data_generation import load_cases_csv
from .models import Action, InvoiceCase
from .policies import (
    baseline_action,
    expected_costs,
    policy_a_action,
    policy_b_action,
)


PolicyFunction = Callable[[InvoiceCase, Mapping[str, Any]], Action]


def _baseline_policy(case: InvoiceCase, _: Mapping[str, Any]) -> Action:
    return baseline_action(case)


def _belief_policy_a(case: InvoiceCase, config: Mapping[str, Any]) -> Action:
    evidence = case.observation()
    return policy_a_action(calculate_beliefs(evidence, config), config, evidence)


def _belief_policy_b(case: InvoiceCase, config: Mapping[str, Any]) -> Action:
    evidence = case.observation()
    return policy_b_action(calculate_beliefs(evidence, config), config, evidence)


POLICIES: dict[str, PolicyFunction] = {
    "baseline": _baseline_policy,
    "policy_a": _belief_policy_a,
    "policy_b": _belief_policy_b,
}


def _explanation(policy: str, action: Action, case: InvoiceCase) -> str:
    if policy == "baseline":
        if case.duplicate_invoice_signal:
            return "Baseline rule: duplicate invoice signal triggered HOLD."
        if case.bank_account_changed:
            return "Baseline rule: bank account change triggered VERIFY."
        if case.lookalike_domain_signal or case.unusual_urgency:
            return "Baseline rule: suspicious communication signal triggered ESCALATE."
        return "Baseline rule: no configured warning rule triggered; APPROVE."
    return f"{policy} selected {action.value} using beliefs, costs, and thresholds."


def run_experiment(
    cases_path: str | Path = "data/cases.csv",
    config_path: str | Path = "config/simulation_assumptions.json",
    output_dir: str | Path = "results",
) -> list[dict[str, Any]]:
    """Run all policies on every case and save JSON and CSV results."""

    cases = load_cases_csv(cases_path)
    config = load_assumptions(config_path)
    results: list[dict[str, Any]] = []

    for case in cases:
        observation = case.observation()
        beliefs = calculate_beliefs(observation, config)
        costs = expected_costs(beliefs, config["costs"])
        for policy_name, policy in POLICIES.items():
            action = policy(case, config)
            actual_cost = float(config["costs"][action.value][case.true_state.value])
            results.append(
                {
                    "case_id": case.case_id,
                    "policy": policy_name,
                    "evidence": observation,
                    "true_state": case.true_state.value,
                    "beliefs": {state.value: probability for state, probability in beliefs.items()},
                    "action": action.value,
                    "expected_cost": round(costs[action], 6),
                    "actual_cost": actual_cost,
                    "human_review_required": action in {Action.HOLD, Action.ESCALATE},
                    "explanation": _explanation(policy_name, action, case),
                }
            )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    _save_json(results, output_path / "experiment_results.json")
    _save_summary_csv(results, output_path / "experiment_summary.csv")
    return results


def _save_json(results: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
        file.write("\n")


def _save_summary_csv(results: list[dict[str, Any]], path: Path) -> None:
    fields = [
        "case_id",
        "policy",
        "true_state",
        "legitimate_probability",
        "error_probability",
        "fraud_probability",
        "action",
        "expected_cost",
        "actual_cost",
        "human_review_required",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "case_id": result["case_id"],
                    "policy": result["policy"],
                    "true_state": result["true_state"],
                    "legitimate_probability": result["beliefs"]["LEGITIMATE"],
                    "error_probability": result["beliefs"]["ERROR"],
                    "fraud_probability": result["beliefs"]["FRAUD"],
                    "action": result["action"],
                    "expected_cost": result["expected_cost"],
                    "actual_cost": result["actual_cost"],
                    "human_review_required": str(
                        result["human_review_required"]
                    ).lower(),
                }
            )
