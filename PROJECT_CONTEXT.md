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

Not completed:

- Probability model and configurable assumptions.
- Configuration file for priors, likelihoods, costs, and thresholds.
- Synthetic 40-case dataset.
- Experiment runner and result files.
- Metrics, failure analysis, and figures.
- Additional automated tests for the probability model, policies, feedback,
  experiments, and metrics.
- README and research documentation.
- IJCAI-style preprint.
- Genuine Reddit/X discussions and AI reviews.
- Verified references.

Verification note:

- `python3 -m invoice_agent` succeeds with `PYTHONPATH=src`.
- Python source compilation succeeds.
- The virtual environment contains the development dependencies.
- `python -m pytest` passes: 6 tests passed.

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

Implement the configurable priors and likelihood-based belief model, with
tests for normalization and evidence updates.

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
