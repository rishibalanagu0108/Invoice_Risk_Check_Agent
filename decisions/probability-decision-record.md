# Probability Decision Record

Status: generated from executed synthetic experiment output

This is one modeled case from `data/cases.csv`. All probabilities, likelihoods,
and costs are configurable simulation assumptions. They are not real-world
fraud statistics or financial estimates.

## Audit data

| Item | Value |
|---|---|
| Case | `case-006` |
| Dataset | `data/cases.csv` |
| True state | `ERROR` (evaluation-only label, hidden at decision time) |
| Model version | `Version 1 + Model Revision 001` |
| Policy | `Policy B / risk_sensitive` |
| Evidence event | Independent callback denies expected verification |
| Record date | `2026-08-20` |

## Initial decision

### Evidence observed

Relevant evidence at decision time:

```text
invoice_amount = 1100.0
historical_average_amount = 500.0
amount_deviation_ratio = 2.20
amount_unusual = True
purchase_order_match = False
vendor_contact_verified = False
multiple_high_risk_signals = True
callback_verified = None
true_state = hidden from the agent
```

### Hidden states

The possible explanations are:

- `LEGITIMATE`
- `ERROR`
- `FRAUD`

The evaluator later records the synthetic label as `ERROR`, but
the agent does not receive this label before deciding.

### Initial beliefs

The posterior distribution after the initial evidence is:

- `LEGITIMATE`: 0.118149 (11.81%)
- `ERROR`: 0.847775 (84.78%)
- `FRAUD`: 0.034076 (3.41%)

The probabilities sum to `1.000000`.

### Available actions and expected costs

| Action | Expected cost |
|---|---:|
| `APPROVE` | 24.601938 |
| `VERIFY` | 7.713703 |
| `HOLD` | 8.724819 |
| `ESCALATE` | 9.931849 |

### Initial policy decision

Policy B uses the configured risk-sensitive thresholds and safety gate. Because
the case contains multiple high-risk signals, direct approval is not allowed.
The selected action is:

```text
VERIFY
```

## New evidence and posterior update

The simulated verification step returns:

```text
callback_verified = false
```

Modeled likelihoods for this new evidence are:

| Hidden state | P(callback_verified=false given state) |
|---|---:|
| `LEGITIMATE` | 0.05 |
| `ERROR` | 0.25 |
| `FRAUD` | 0.9 |

These are explicitly modeled assumptions from the configuration file.

The posterior distribution after the callback is:

- `LEGITIMATE`: 0.023771 (2.38%)
- `ERROR`: 0.852826 (85.28%)
- `FRAUD`: 0.123403 (12.34%)

The probabilities sum to `1.000000`.

### Updated expected costs

| Action | Expected cost after callback |
|---|---:|
| `APPROVE` | 33.660973 |
| `VERIFY` | 8.175494 |
| `HOLD` | 7.796185 |
| `ESCALATE` | 9.753194 |

The updated Policy B action is:

```text
HOLD
```

## Decision interpretation

The negative callback increases the modeled fraud probability and makes
`HOLD` preferable to continued verification under the risk-sensitive policy.
This is a simulation result for one synthetic case. It does not establish that
these likelihoods are valid in a real payment system.
