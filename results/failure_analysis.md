# Failure Analysis

This report is generated from executed experiment output. The cases are
synthetic and the costs are normalized simulation assumptions.

Highest observed failure cost: `100.0` (case-004 / baseline).

| Case | Policy | True state | Action | Expected action | Cost | Failure condition |
|---|---|---|---|---|---:|---|
| case-004 | baseline | FRAUD | APPROVE | HOLD | 100.0 | false approval of fraud |
| case-004 | policy_a | FRAUD | APPROVE | HOLD | 100.0 | false approval of fraud |
| case-004 | policy_b | FRAUD | APPROVE | HOLD | 100.0 | false approval of fraud |
| case-007 | policy_a | FRAUD | APPROVE | HOLD | 100.0 | false approval of fraud |
| case-007 | policy_b | FRAUD | APPROVE | HOLD | 100.0 | false approval of fraud |

## Improvement notes

### case-004 / baseline

- Why it happened: Baseline rule: no configured warning rule triggered; APPROVE.
- Possible improvement: Add stronger fraud evidence, lower the approval threshold, or require verification before approval.

### case-004 / policy_a

- Why it happened: policy_a selected APPROVE using beliefs, costs, and thresholds.
- Possible improvement: Add stronger fraud evidence, lower the approval threshold, or require verification before approval.

### case-004 / policy_b

- Why it happened: policy_b selected APPROVE using beliefs, costs, and thresholds.
- Possible improvement: Add stronger fraud evidence, lower the approval threshold, or require verification before approval.

### case-007 / policy_a

- Why it happened: policy_a selected APPROVE using beliefs, costs, and thresholds.
- Possible improvement: Add stronger fraud evidence, lower the approval threshold, or require verification before approval.

### case-007 / policy_b

- Why it happened: policy_b selected APPROVE using beliefs, costs, and thresholds.
- Possible improvement: Add stronger fraud evidence, lower the approval threshold, or require verification before approval.
