# Invoice / Payment Risk Agent

An explainable, small Python agent that evaluates vendor invoices and payment
requests under uncertainty.

The agent observes invoice, vendor, payment, historical, and verification
evidence. It estimates three hidden states:

- `LEGITIMATE`
- `ERROR`
- `FRAUD`

It chooses one action:

- `APPROVE`
- `VERIFY`
- `HOLD`
- `ESCALATE`

This is a course project using synthetic data and configurable simulation
assumptions. It must not autonomously release real payments.

## Architecture

```text
data/cases.csv
    ↓
InvoiceCase and prediction-time observation
    ↓
Belief model: P(LEGITIMATE), P(ERROR), P(FRAUD)
    ↓
Baseline / Policy A / Policy B
    ↓
Action, expected cost, actual evaluation cost
    ↓
Metrics and failure analysis
```

`true_state` is stored for evaluation but excluded from the agent observation.
The feedback experiment simulates a verification callback and records initial
and post-feedback decisions separately.

## Setup

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## Launch the Streamlit showcase

Install the UI extra:

```bash
python -m pip install -e '.[dev,ui]'
```

Launch the app:

```bash
streamlit run app.py
```

The interface supports case and policy selection, belief and expected-cost
display, evidence inspection, simulated callback feedback, dataset viewing,
and result/failure-report viewing. The UI calls the same deterministic agent
functions used by the command-line experiments.

## Run tests

```bash
python -m pytest
```

Run one test module:

```bash
python -m pytest tests/test_beliefs.py
```

## Regenerate data and results

Generate the deterministic 40-case CSV dataset:

```bash
PYTHONPATH=src python -m invoice_agent.data_generation
```

Run the experiment:

```bash
PYTHONPATH=src python experiments/run_experiment.py
```

Calculate metrics:

```bash
PYTHONPATH=src python experiments/calculate_metrics.py
```

Generate failure analysis:

```bash
PYTHONPATH=src python experiments/analyze_failures.py
```

Run the feedback experiment:

```bash
PYTHONPATH=src python experiments/run_feedback.py
```

Generate the probability decision record:

```bash
PYTHONPATH=src python experiments/create_probability_record.py
```

Generated outputs are written under `results/` and can be regenerated from the
tracked code, configuration, dataset, and commands above.

## Repository structure

```text
config/       Simulation priors, likelihoods, costs, and thresholds
data/         Canonical synthetic CSV dataset and schema notes
decisions/    Design decisions, revisions, and probability record
experiments/  Reproducible experiment/reporting entry points
results/      Generated experiment, metrics, feedback, and failure outputs
src/          Agent implementation
tests/        Automated tests
paper/        IJCAI-style preprint files and figures
social/       Evidence-backed social-post templates
```

## Main components

- `models.py`: case schema, hidden states, actions, validation, and observation
  view.
- `beliefs.py`: configurable Bayesian-style belief update.
- `policies.py`: costs, baseline, efficiency policy, and risk-sensitive policy.
- `data_generation.py`: seeded generation and CSV loading.
- `experiment.py`: runs all three systems on all 40 cases.
- `metrics.py`: action rates, costs, confusion tables, and fraud-response
  metrics.
- `feedback.py`: simulated callback and post-feedback decision.
- `analysis.py`: failure report from actual experiment output.

## Assumptions and limitations

- Probabilities and costs are simulation assumptions, not empirical estimates.
- Evidence is initially treated as conditionally independent.
- The synthetic dataset is not real-world fraud evidence.
- The callback is a simulation oracle, not a production verification service.
- The policies are deliberately simple and require sensitivity analysis.
- An LLM/API is not required for the core decision pipeline.
- Human review and proper payment controls remain necessary.

## Ethics and human control

False fraud approvals can cause financial harm. False holds can delay legitimate
vendors. Automation bias, privacy, explanation quality, and review capacity
must be considered before deployment. Synthetic results cannot establish real
fraud probabilities. The agent should not autonomously release payments.

## AI-use statement

AI tools assisted with project planning, research preparation, software
development, debugging, experiment tooling, documentation, LaTeX preparation,
and review-prompt preparation. Human discussions must be genuine, citations
must be manually verified, experiment claims must come from executed commands,
and the student remains responsible for the final content.

## Human-discussion status

No Reddit/X discussions or practitioner reviews have been fabricated. See
`discussion-record.md` and `review-record.md` for templates and current TODOs.
