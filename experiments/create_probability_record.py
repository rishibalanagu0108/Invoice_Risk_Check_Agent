"""Create the reproducible probability decision record for one case."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from invoice_agent.beliefs import calculate_beliefs, load_assumptions
from invoice_agent.data_generation import load_cases_csv
from invoice_agent.policies import expected_costs, policy_b_action


def _distribution(beliefs: dict) -> str:
    return "\n".join(
        f"- `{state.value}`: {probability:.6f} ({probability:.2%})"
        for state, probability in beliefs.items()
    )


def create_record(
    case_id: str = "case-006",
    cases_path: str | Path = "data/cases.csv",
    config_path: str | Path = "config/simulation_assumptions.json",
    output_path: str | Path = "decisions/probability-decision-record.md",
) -> None:
    config = load_assumptions(config_path)
    case = next(case for case in load_cases_csv(cases_path) if case.case_id == case_id)
    initial_beliefs = calculate_beliefs(case.observation(), config)
    initial_costs = expected_costs(initial_beliefs, config["costs"])
    initial_action = policy_b_action(initial_beliefs, config, case.observation())

    callback_verified = False
    updated_case = replace(case, callback_verified=callback_verified)
    posterior = calculate_beliefs(updated_case.observation(), config)
    posterior_costs = expected_costs(posterior, config["costs"])
    post_action = policy_b_action(posterior, config, updated_case.observation())

    likelihood = config["likelihoods"]["callback_verified"]["false"]
    evidence = case.observation()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f"""# Probability Decision Record

Status: generated from executed synthetic experiment output

This is one modeled case from `data/cases.csv`. All probabilities, likelihoods,
and costs are configurable simulation assumptions. They are not real-world
fraud statistics or financial estimates.

## Audit data

| Item | Value |
|---|---|
| Case | `{case.case_id}` |
| Dataset | `data/cases.csv` |
| True state | `{case.true_state.value}` (evaluation-only label, hidden at decision time) |
| Model version | `Version 1 + Model Revision 001` |
| Policy | `Policy B / risk_sensitive` |
| Evidence event | Independent callback denies expected verification |
| Record date | `2026-08-20` |

## Initial decision

### Evidence observed

Relevant evidence at decision time:

```text
invoice_amount = {evidence['invoice_amount']}
historical_average_amount = {evidence['historical_average_amount']}
amount_deviation_ratio = {evidence['amount_deviation_ratio']:.2f}
amount_unusual = {evidence['amount_unusual']}
purchase_order_match = {evidence['purchase_order_match']}
vendor_contact_verified = {evidence['vendor_contact_verified']}
multiple_high_risk_signals = {evidence['multiple_high_risk_signals']}
callback_verified = {evidence['callback_verified']}
true_state = hidden from the agent
```

### Hidden states

The possible explanations are:

- `LEGITIMATE`
- `ERROR`
- `FRAUD`

The evaluator later records the synthetic label as `{case.true_state.value}`, but
the agent does not receive this label before deciding.

### Initial beliefs

The posterior distribution after the initial evidence is:

{_distribution(initial_beliefs)}

The probabilities sum to `{sum(initial_beliefs.values()):.6f}`.

### Available actions and expected costs

| Action | Expected cost |
|---|---:|
| `APPROVE` | {initial_costs[next(a for a in initial_costs if a.value == 'APPROVE')]:.6f} |
| `VERIFY` | {initial_costs[next(a for a in initial_costs if a.value == 'VERIFY')]:.6f} |
| `HOLD` | {initial_costs[next(a for a in initial_costs if a.value == 'HOLD')]:.6f} |
| `ESCALATE` | {initial_costs[next(a for a in initial_costs if a.value == 'ESCALATE')]:.6f} |

### Initial policy decision

Policy B uses the configured risk-sensitive thresholds and safety gate. Because
the case contains multiple high-risk signals, direct approval is not allowed.
The selected action is:

```text
{initial_action.value}
```

## New evidence and posterior update

The simulated verification step returns:

```text
callback_verified = false
```

Modeled likelihoods for this new evidence are:

| Hidden state | P(callback_verified=false given state) |
|---|---:|
| `LEGITIMATE` | {likelihood['LEGITIMATE']} |
| `ERROR` | {likelihood['ERROR']} |
| `FRAUD` | {likelihood['FRAUD']} |

These are explicitly modeled assumptions from the configuration file.

The posterior distribution after the callback is:

{_distribution(posterior)}

The probabilities sum to `{sum(posterior.values()):.6f}`.

### Updated expected costs

| Action | Expected cost after callback |
|---|---:|
| `APPROVE` | {posterior_costs[next(a for a in posterior_costs if a.value == 'APPROVE')]:.6f} |
| `VERIFY` | {posterior_costs[next(a for a in posterior_costs if a.value == 'VERIFY')]:.6f} |
| `HOLD` | {posterior_costs[next(a for a in posterior_costs if a.value == 'HOLD')]:.6f} |
| `ESCALATE` | {posterior_costs[next(a for a in posterior_costs if a.value == 'ESCALATE')]:.6f} |

The updated Policy B action is:

```text
{post_action.value}
```

## Decision interpretation

The negative callback increases the modeled fraud probability and makes
`HOLD` preferable to continued verification under the risk-sensitive policy.
This is a simulation result for one synthetic case. It does not establish that
these likelihoods are valid in a real payment system.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    create_record()
    print("Saved decisions/probability-decision-record.md")
