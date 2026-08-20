# Failure Analysis

This report is generated from executed experiment output. The cases are
synthetic and the costs are normalized simulation assumptions.

Highest observed failure cost: `100.0` (case-004 / baseline).

| Case | Policy | True state | Action | Expected action | Cost | Failure condition |
|---|---|---|---|---|---:|---|
| case-004 | baseline | FRAUD | APPROVE | HOLD | 100.0 | false approval of fraud |
| case-024 | baseline | FRAUD | APPROVE | HOLD | 100.0 | false approval of fraud |
| case-006 | baseline | ERROR | APPROVE | VERIFY, HOLD | 25.0 | operational error approved |
| case-011 | baseline | ERROR | APPROVE | VERIFY, HOLD | 25.0 | operational error approved |
| case-011 | policy_a | ERROR | APPROVE | VERIFY, HOLD | 25.0 | operational error approved |

## Improvement notes

### case-004 / baseline

- Why it happened: Baseline rule: no configured warning rule triggered; APPROVE.
- Possible improvement: Add stronger fraud evidence, lower the approval threshold, or require verification before approval.

### case-024 / baseline

- Why it happened: Baseline rule: no configured warning rule triggered; APPROVE.
- Possible improvement: Add stronger fraud evidence, lower the approval threshold, or require verification before approval.

### case-006 / baseline

- Why it happened: Baseline rule: no configured warning rule triggered; APPROVE.
- Possible improvement: Add stronger anomaly checks and route mismatches to verification before approval.

### case-011 / baseline

- Why it happened: Baseline rule: no configured warning rule triggered; APPROVE.
- Possible improvement: Add stronger anomaly checks and route mismatches to verification before approval.

### case-011 / policy_a

- Why it happened: policy_a selected APPROVE using beliefs, costs, and thresholds.
- Possible improvement: Add stronger anomaly checks and route mismatches to verification before approval.
