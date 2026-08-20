"""Failure analysis derived from executed experiment results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .models import Action, HiddenState


def _optimal_actions(
    true_state: str, costs: Mapping[str, Mapping[str, float]]
) -> list[str]:
    state_costs = {
        action.value: float(costs[action.value][true_state]) for action in Action
    }
    minimum = min(state_costs.values())
    return [action for action, cost in state_costs.items() if cost == minimum]


def _failure_condition(true_state: str, action: str) -> tuple[str, str]:
    if true_state == HiddenState.FRAUD.value and action == Action.APPROVE.value:
        return (
            "false approval of fraud",
            "Add stronger fraud evidence, lower the approval threshold, or require verification before approval.",
        )
    if true_state == HiddenState.FRAUD.value:
        return (
            "missed fraud protection",
            "Treat the fraud signal as insufficiently resolved and route the case to verification, hold, or escalation.",
        )
    if true_state == HiddenState.LEGITIMATE.value and action != Action.APPROVE.value:
        return (
            "unnecessary intervention on legitimate payment",
            "Improve evidence quality or raise the intervention threshold for low-risk legitimate cases.",
        )
    if true_state == HiddenState.ERROR.value and action == Action.APPROVE.value:
        return (
            "operational error approved",
            "Add stronger anomaly checks and route mismatches to verification before approval.",
        )
    return (
        "higher-cost action than available alternative",
        "Compare the action cost assumptions and expand the policy action rules.",
    )


def identify_failures(
    results: Iterable[dict[str, Any]],
    config: Mapping[str, Any],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Select the highest-cost incorrect decisions from executed results."""

    candidates: list[dict[str, Any]] = []
    for result in results:
        true_state = result["true_state"]
        action = result["action"]
        optimal_actions = _optimal_actions(true_state, config["costs"])
        actual_cost = float(result["actual_cost"])
        if action in optimal_actions:
            continue
        condition, improvement = _failure_condition(true_state, action)
        candidates.append(
            {
                "case_id": result["case_id"],
                "policy": result["policy"],
                "true_state": true_state,
                "evidence": result["evidence"],
                "beliefs": result["beliefs"],
                "action": action,
                "expected_action": optimal_actions,
                "failure_condition": condition,
                "why_it_happened": result["explanation"],
                "actual_cost": actual_cost,
                "possible_improvement": improvement,
            }
        )
    candidates.sort(key=lambda failure: failure["actual_cost"], reverse=True)
    return candidates[: max(limit, 5)]


def highest_cost_failure(failures: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Return the highest-cost item from a failure report."""

    failures = list(failures)
    if not failures:
        raise ValueError("no failures available")
    return max(failures, key=lambda failure: failure["actual_cost"])


def save_failure_report(
    results_path: str | Path = "results/experiment_results.json",
    config_path: str | Path = "config/simulation_assumptions.json",
    output_dir: str | Path = "results",
) -> list[dict[str, Any]]:
    """Create JSON and Markdown failure reports from actual results."""

    results = json.loads(Path(results_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    failures = identify_failures(results, config)
    highest = highest_cost_failure(failures)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    report = {
        "source_results": str(results_path),
        "failure_count": len(failures),
        "highest_cost_failure": highest,
        "failures": failures,
    }
    (output / "failure_analysis.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    _write_markdown(report, output / "failure_analysis.md")
    return failures


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Failure Analysis",
        "",
        "This report is generated from executed experiment output. The cases are",
        "synthetic and the costs are normalized simulation assumptions.",
        "",
        f"Highest observed failure cost: `{report['highest_cost_failure']['actual_cost']}` "
        f"({report['highest_cost_failure']['case_id']} / {report['highest_cost_failure']['policy']}).",
        "",
        "| Case | Policy | True state | Action | Expected action | Cost | Failure condition |",
        "|---|---|---|---|---|---:|---|",
    ]
    for failure in report["failures"]:
        expected = ", ".join(failure["expected_action"])
        lines.append(
            f"| {failure['case_id']} | {failure['policy']} | {failure['true_state']} | "
            f"{failure['action']} | {expected} | {failure['actual_cost']} | "
            f"{failure['failure_condition']} |"
        )
    lines.extend(["", "## Improvement notes", ""])
    for failure in report["failures"]:
        lines.extend(
            [
                f"### {failure['case_id']} / {failure['policy']}",
                "",
                f"- Why it happened: {failure['why_it_happened']}",
                f"- Possible improvement: {failure['possible_improvement']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
