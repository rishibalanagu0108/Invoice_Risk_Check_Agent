# Invoice / Payment Risk Agent — Project Context

## How to resume this project

Read these files in order at the beginning of a new session:

1. `PROJECT_CONTEXT.md` — current project memory and next action.
2. `starter.txt` — complete assignment requirements.
3. `decisions/design-specification.md` — agreed Version-1 architecture.
4. `decisions/commit-plan.md` — planned feature commits.

Before changing anything, check the working tree with:

```bash
git status --short --branch
```

## Project objective

Build a small, explainable Python agent that evaluates vendor invoices and
payment requests under uncertainty.

The agent observes invoice, vendor, payment, historical, and verification
evidence. It estimates three hidden states:

- `LEGITIMATE`
- `ERROR`
- `FRAUD`

It must choose one action:

- `APPROVE`
- `VERIFY`
- `HOLD`
- `ESCALATE`

The system must make an operational action, not only generate an explanation.

## Current status

Completed:

- Read and understood the assignment in `starter.txt`.
- Reviewed the user-created tldraw architecture for the project.
- Created `decisions/design-specification.md`.
- Chosen a simple, interpretable Bayesian-style belief model for Version 1.
- Defined a configurable normalized cost matrix.
- Defined a simple baseline and two belief-based policies.
- Defined the verification feedback loop.
- Scaffolded the Python package and project directories.
- Added `pyproject.toml` with the project metadata and pytest configuration.
- Added a package entry point and a minimal scaffold import test.
- Added typed invoice cases, hidden states, and allowed actions.
- Added validation and a prediction-time observation view that excludes the
  hidden evaluation label.
- Added configurable priors and evidence likelihoods.
- Added Bayesian-style belief updates with normalization and evidence tests.
- Added normalized action/state costs and expected-cost calculations.
- Added the rule-based baseline plus efficiency and risk-sensitive policies.
- Verified that policy thresholds create distinct approval behavior while costs
  select among safer actions.
- Added a seeded generator for exactly 40 varied synthetic cases.
- Saved canonical `data/cases.csv` with 16 legitimate, 12 error, and 12 fraud
  cases.
- Added CSV type conversion and round-trip validation.
- Added an experiment runner for the baseline, Policy A, and Policy B.
- Generated 120 decision records from the 40 cases and saved JSON/CSV result
  outputs under `results/`.
- Added policy-level metrics, action rates, review rate, state/action
  confusion matrices, fraud-protective precision/recall, and cost summaries.
- Added simulated callback feedback with separate initial and post-feedback
  decisions.
- Generated 8 feedback records: 6 baseline verifications and 2 Policy B
  verifications; both Policy B records changed from VERIFY to HOLD after a
  negative callback.
- Added failure analysis generated from executed experiment output.
- Identified 5 highest-cost incorrect decisions; the highest observed cost was
  100 for approving fraud in `case-004` (tied by other fraud approvals).
- Applied Model Revision 001 using the failure findings: derived risk evidence,
  revised duplicate likelihoods, and safety gates for duplicate/multiple-risk
  cases.
- Re-ran the experiment, metrics, and failure analysis after the revision.
- Added a reproducible probability decision record for `case-006`, showing
  VERIFY before callback evidence and HOLD after a negative callback.
- Added README, research, discussion, review, social-template, and completion
  checklist documentation with unsupported claims marked TODO.
- Added a Streamlit showcase that calls the existing agent logic for case
  decisions, feedback, dataset inspection, and result viewing.
- Added showcase `case-008`: a legitimate case that transitions from VERIFY to
  APPROVE after successful verification clears the duplicate signal.
- Verified Streamlit startup on localhost and verified 38 passing tests.

Not completed:

- Figures.
- IJCAI-style preprint.
- Genuine Reddit/X discussions and AI reviews.
- Verified references.

Verification note:

- `python3 -m invoice_agent` succeeds with `PYTHONPATH=src`.
- Python source compilation succeeds.
- The virtual environment contains the development dependencies.
- `python -m pytest` passes: 38 tests passed.
- The experiment runner saves generated outputs to `results/`. These generated
  result files are currently untracked and can either be committed as the
  executed run artifact or regenerated from the recorded commands.

Initial metrics observation from the executed simulation:

- Baseline: total cost 520, fraud recall 0.583, human-review rate 0.275.
- Policy A: total cost 1500, fraud recall 0.0, human-review rate 0.0.
- Policy B: total cost 1320, fraud recall 0.0, human-review rate 0.0.

This indicates that the current likelihood assumptions produce fraud beliefs
below the policy thresholds for the generated fraud cases. It is an actual
observed model/design failure to analyze, not a final real-world claim.

Post-revision metrics from the executed simulation:

- Baseline: total cost 520, fraud recall 0.583, human-review rate 0.275.
- Policy A: total cost 224, fraud recall 1.0, human-review rate 0.3.
- Policy B: total cost 224, fraud recall 1.0, human-review rate 0.3.

The revision improved the simulated policy results, but these remain
assumption-dependent synthetic findings and require sensitivity analysis.

## Core architecture

```text
Case data
  → evidence features
  → belief model
  → P(LEGITIMATE), P(ERROR), P(FRAUD)
  → cost-sensitive policy
  → action + explanation
  → optional verification feedback
  → updated beliefs and next action
```

The baseline is a separate comparison system. It uses fixed rules and does not
use probabilities or costs. Policy A and Policy B use the common belief model,
cost matrix, and configurable policy thresholds.

## Current design assumptions

- Python is the implementation language.
- Version 1 uses an interpretable likelihood-based update.
- Priors and likelihoods are simulation assumptions unless later supported by
  verified research.
- Cost values are normalized experimental scores, not financial estimates.
- The first dataset contains exactly 40 synthetic labeled cases.
- The hidden state is available to evaluation code only after prediction.
- Evidence items are initially treated as conditionally independent.
- Verification can produce new evidence and trigger a second decision.
- The agent must not autonomously release real payments.
- Human discussions, citations, reviews, and results must never be fabricated.

## Current provisional cost matrix

| Action | Legitimate | Error | Fraud |
|---|---:|---:|---:|
| `APPROVE` | 0 | 25 | 100 |
| `VERIFY` | 5 | 8 | 10 |
| `HOLD` | 15 | 8 | 5 |
| `ESCALATE` | 10 | 10 | 8 |

These values are configurable and should be sensitivity-tested after the first
experiment.

## Integrity rules

- Do not claim a test passed unless it was actually run.
- Do not invent experiment results.
- Do not invent human conversations or social-media responses.
- Do not invent citations, papers, accounts, or communities.
- Clearly label synthetic data and modeled probabilities.
- Keep the implementation small and understandable.

## Immediate next action

If UI work is complete, return to the paused preprint/research tasks: create the
IJCAI-style course preprint scaffold and verify the official author kit status.

## Expected future top-level structure

```text
README.md
PROJECT_CONTEXT.md
starter.txt
research-file.md
discussion-record.md
review-record.md
requirements.txt or pyproject.toml
paper/
src/
data/
experiments/
results/
decisions/
social/
tests/
```

Update this file whenever a major design decision, experiment result, failure,
or project milestone changes the project state.
