# Invoice / Payment Risk Agent — Version 1 Design Specification

Status: Initial working specification

This document defines the smallest useful version of the invoice/payment-risk
agent. All numerical values in this version are configurable simulation
assumptions. They are not financial estimates or empirically validated fraud
statistics.

## 1. Objective

Given an invoice/payment case and the evidence available at decision time, the
agent estimates three mutually exclusive hidden states and selects one action:

- `LEGITIMATE`: the payment request is genuine and should proceed.
- `ERROR`: the request contains an innocent mistake or operational anomaly.
- `FRAUD`: the request is intentionally deceptive or unauthorized.

Available actions:

- `APPROVE`: allow the payment to proceed.
- `VERIFY`: obtain independent evidence before deciding again.
- `HOLD`: temporarily stop the payment while the issue is investigated.
- `ESCALATE`: send the case to a human reviewer.

The agent must return an action, not only a written explanation.

## 2. Decision boundary

The agent sees the case evidence but not the true hidden state. The experiment
runner stores the true state separately and reveals it only after prediction so
that decisions can be evaluated.

```text
Case evidence
    ↓
Belief model: P(LEGITIMATE), P(ERROR), P(FRAUD)
    ↓
Cost-sensitive policy
    ↓
Action + explanation
    ↓
Optional verification feedback
    ↓
Updated evidence and beliefs
```

## 3. Initial case schema

Each synthetic case will contain the following fields. Boolean fields use
`true`, `false`, or `null` when the evidence is unavailable.

| Field | Type | Meaning |
|---|---|---|
| `case_id` | string | Stable identifier for the case. |
| `vendor_id` | string | Vendor identifier. |
| `vendor_age_days` | integer | Age of the vendor relationship. |
| `existing_vendor` | boolean | Whether the vendor is already known. |
| `invoice_amount` | number | Amount requested. |
| `historical_average_amount` | number | Historical average for comparison. |
| `bank_account_changed` | boolean | Whether payment bank details recently changed. |
| `bank_change_age_days` | integer/null | Days since the bank change, if applicable. |
| `email_domain_changed` | boolean | Whether the contact email domain changed. |
| `lookalike_domain_signal` | boolean | Whether the domain resembles a trusted domain suspiciously. |
| `invoice_number_pattern_valid` | boolean | Whether the invoice number follows expected patterns. |
| `duplicate_invoice_signal` | boolean | Whether a duplicate invoice is suspected. |
| `purchase_order_match` | boolean | Whether the invoice matches a purchase order. |
| `payment_terms_match` | boolean | Whether payment terms match the vendor record. |
| `unusual_urgency` | boolean | Whether the request contains unusual urgency. |
| `location_changed` | boolean | Whether country/location information changed unexpectedly. |
| `vendor_contact_verified` | boolean | Whether the vendor contact was independently verified. |
| `callback_verified` | boolean/null | Result of an independent callback, if performed. |
| `supporting_documents_available` | boolean | Whether supporting documents are available. |
| `true_state` | enum | Evaluation-only label; never passed into prediction. |

The feature set is deliberately extensible. Feedback may lead to new fields,
removed fields, or revised feature definitions.

## 4. Belief model

Version 1 will use an interpretable likelihood-based update.

Let the hidden states be `L` (legitimate), `E` (error), and `F` (fraud). For
observed evidence `e`, the model uses:

```text
unnormalized_belief(state) = prior(state) × likelihood(e | state)

P(state | e) = unnormalized_belief(state)
                / sum(all unnormalized_beliefs)
```

For multiple independent evidence items, the configurable likelihood values are
multiplied. The independence assumption is a simplification and will be listed
as a limitation.

The output must always contain exactly:

```text
P(LEGITIMATE) + P(ERROR) + P(FRAUD) = 1.0
```

Priors and likelihoods will live in configuration rather than being hidden in
the implementation. Example values may be used only as labeled simulation
assumptions.

## 5. Cost model

The experiment will use normalized costs, not real currency values. Initial
values are provisional and should be sensitivity-tested.

| Action | Legitimate | Error | Fraud |
|---|---:|---:|---:|
| `APPROVE` | 0 | 25 | 100 |
| `VERIFY` | 5 | 8 | 10 |
| `HOLD` | 15 | 8 | 5 |
| `ESCALATE` | 10 | 10 | 8 |

Interpretation:

- Approving fraud is highly costly.
- Verifying a legitimate payment causes a smaller operational cost.
- Holding a legitimate payment causes delay.
- Escalation consumes human-review capacity.

These values are not claims about actual business losses. They exist to make
the decision trade-offs testable and will be stored in configuration.

## 6. Policies

### Baseline

The baseline is a simple rule system and does not calculate a full belief
distribution:

1. If a duplicate signal is present, return `HOLD`.
2. Else if bank details changed, return `VERIFY`.
3. Else if a lookalike domain or unusual urgency is present, return `ESCALATE`.
4. Otherwise, return `APPROVE`.

### Policy A — efficiency-oriented

Policy A favors approval when evidence is mostly reassuring and uses `VERIFY`
for moderate uncertainty. It may use `HOLD` or `ESCALATE` only when fraud belief
is high or the expected cost of approval is clearly worse.

The exact thresholds will be kept in configuration. The policy will be
evaluated for approval rate, review rate, and missed-fraud cost.

### Policy B — risk-sensitive

Policy B gives greater weight to avoiding costly fraudulent approvals. It uses
`VERIFY`, `HOLD`, or `ESCALATE` at lower fraud-belief thresholds than Policy A.

The policies will select actions by comparing expected action cost:

```text
expected_cost(action) =
    sum(P(state | evidence) × cost(action, state))
```

Thresholds may restrict or order actions so that the two policies remain
meaningfully distinct and understandable.

## 7. Feedback loop

`VERIFY` is an evidence-gathering action rather than a final truth claim:

```text
Initial case
    ↓
VERIFY
    ↓
Independent callback / vendor confirmation
    ↓
callback_verified = true or false
    ↓
Posterior belief update
    ↓
Policy selects the next action
```

The experiment output will keep the initial and post-feedback decisions as
separate records.

## 8. Human reasoning function

The agent will identify uncertainty and request additional evidence before a
high-cost decision. In Version 1 this is implemented through `VERIFY` and
`ESCALATE`:

- `VERIFY` requests an independent check when more evidence could change the
  decision.
- `ESCALATE` requests human judgment when the estimated consequences are high
  or evidence remains conflicting.

The system must not autonomously release real payments.

## 9. Experiment requirements

The first experiment will generate exactly 40 labeled synthetic cases with
variety across hidden states, evidence patterns, amounts, ambiguity, and
verification outcomes. Each case will be evaluated by the baseline, Policy A,
and Policy B.

The experiment will save machine-readable results containing the case ID,
evidence, hidden state, beliefs, action, expected cost, actual cost, review
requirement, policy, and explanation.

## 10. Open decisions before implementation

- Final prior and likelihood values, clearly marked as simulation assumptions.
- Exact thresholds for Policies A and B.
- Whether the initial cost values should be adjusted before the first run.
- Whether any evidence feature should be removed to keep the first version
  small.
- Whether an official IJCAI author kit is available locally.

These decisions can be revised after the first experiment and after genuine
human or practitioner feedback is collected.
