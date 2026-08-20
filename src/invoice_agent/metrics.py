"""Metrics for cost-sensitive invoice-risk decisions."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .models import Action, HiddenState

PROTECTIVE_ACTIONS = {Action.HOLD.value, Action.ESCALATE.value}


def _policy_results(results: Iterable[dict[str, Any]], policy: str) -> list[dict[str, Any]]:
    selected = [result for result in results if result["policy"] == policy]
    if not selected:
        raise ValueError(f"no results found for policy: {policy}")
    return selected


def confusion_matrix(results: Iterable[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Count true hidden states against selected actions."""

    matrix = {
        state.value: {action.value: 0 for action in Action}
        for state in HiddenState
    }
    for result in results:
        matrix[result["true_state"]][result["action"]] += 1
    return matrix


def action_rates(results: list[dict[str, Any]]) -> dict[str, float]:
    """Return the fraction of cases receiving each action."""

    counts = Counter(result["action"] for result in results)
    total = len(results)
    return {action.value.lower(): counts[action.value] / total for action in Action}


def _fraud_protective_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    true_positive = sum(
        result["true_state"] == HiddenState.FRAUD.value
        and result["action"] in PROTECTIVE_ACTIONS
        for result in results
    )
    false_positive = sum(
        result["true_state"] != HiddenState.FRAUD.value
        and result["action"] in PROTECTIVE_ACTIONS
        for result in results
    )
    false_negative = sum(
        result["true_state"] == HiddenState.FRAUD.value
        and result["action"] not in PROTECTIVE_ACTIONS
        for result in results
    )
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


def fraud_precision_recall(results: list[dict[str, Any]]) -> dict[str, float | int]:
    """Measure protective actions as the positive fraud-response class.

    `HOLD` and `ESCALATE` count as protective actions. `VERIFY` is treated as
    an intermediate action and is reported separately through action rates.
    """

    counts = _fraud_protective_counts(results)
    precision_denominator = counts["true_positive"] + counts["false_positive"]
    recall_denominator = counts["true_positive"] + counts["false_negative"]
    return {
        **counts,
        "fraud_precision": (
            counts["true_positive"] / precision_denominator
            if precision_denominator
            else 0.0
        ),
        "fraud_recall": (
            counts["true_positive"] / recall_denominator
            if recall_denominator
            else 0.0
        ),
    }


def cost_summary(results: list[dict[str, Any]]) -> dict[str, float]:
    """Return total, average, and expected average decision cost."""

    actual_costs = [float(result["actual_cost"]) for result in results]
    expected_costs = [float(result["expected_cost"]) for result in results]
    return {
        "total_actual_cost": sum(actual_costs),
        "average_actual_cost": sum(actual_costs) / len(actual_costs),
        "average_expected_cost": sum(expected_costs) / len(expected_costs),
    }


def calculate_policy_metrics(
    results: Iterable[dict[str, Any]], policy: str
) -> dict[str, Any]:
    """Calculate all Version-1 metrics for one policy."""

    selected = _policy_results(results, policy)
    review_count = sum(result["human_review_required"] for result in selected)
    return {
        "policy": policy,
        "case_count": len(selected),
        "action_rates": action_rates(selected),
        "human_review_rate": review_count / len(selected),
        "confusion_matrix": confusion_matrix(selected),
        **fraud_precision_recall(selected),
        **cost_summary(selected),
    }


def calculate_all_metrics(results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Calculate metrics for every policy represented in the results."""

    materialized = list(results)
    policies = sorted({result["policy"] for result in materialized})
    return {
        "policies": {
            policy: calculate_policy_metrics(materialized, policy)
            for policy in policies
        },
        "definitions": {
            "protective_actions": sorted(PROTECTIVE_ACTIONS),
            "false_positive": "non-fraud case receiving HOLD or ESCALATE",
            "false_negative": "fraud case not receiving HOLD or ESCALATE",
            "costs": "normalized simulation costs, not financial estimates",
        },
    }


def save_metrics(metrics: dict[str, Any], path: str | Path) -> None:
    """Save nested metrics as formatted JSON."""

    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
        file.write("\n")


def save_metrics_summary_csv(metrics: dict[str, Any], path: str | Path) -> None:
    """Save one compact policy-level metrics row per CSV record."""

    fields = [
        "policy",
        "case_count",
        "approval_rate",
        "verification_rate",
        "hold_rate",
        "escalation_rate",
        "human_review_rate",
        "fraud_precision",
        "fraud_recall",
        "total_actual_cost",
        "average_actual_cost",
        "average_expected_cost",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for policy_metrics in metrics["policies"].values():
            rates = policy_metrics["action_rates"]
            writer.writerow(
                {
                    "policy": policy_metrics["policy"],
                    "case_count": policy_metrics["case_count"],
                    "approval_rate": rates["approve"],
                    "verification_rate": rates["verify"],
                    "hold_rate": rates["hold"],
                    "escalation_rate": rates["escalate"],
                    "human_review_rate": policy_metrics["human_review_rate"],
                    "fraud_precision": policy_metrics["fraud_precision"],
                    "fraud_recall": policy_metrics["fraud_recall"],
                    "total_actual_cost": policy_metrics["total_actual_cost"],
                    "average_actual_cost": policy_metrics["average_actual_cost"],
                    "average_expected_cost": policy_metrics["average_expected_cost"],
                }
            )
