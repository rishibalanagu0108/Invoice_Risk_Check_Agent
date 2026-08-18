# Feature Commit Plan

The workspace is not currently a Git repository, so these are prepared commit
messages. Initialize Git before using them. Each commit should contain one
coherent feature and its tests or documentation.

## Planned sequence

### 1. Project context and design

```text
docs: define Version 1 agent design
```

Includes the design specification and project context files.

### 2. Project skeleton

```text
chore: scaffold project structure
```

Includes package structure, configuration loading, directories, and initial
dependency metadata.

### 3. Domain data model

```text
feat(data): define invoice risk case model
```

Includes hidden states, actions, case schema, validation, and data dictionary.

### 4. Belief model

```text
feat(agent): add configurable belief model
```

Includes priors, likelihoods, evidence updates, normalization, and belief
explanations.

### 5. Costs and policies

```text
feat(policy): add cost-sensitive decision policies
```

Includes cost matrix, expected-cost calculation, Policy A, Policy B, and the
rule-based baseline.

### 6. Synthetic cases

```text
feat(data): generate reproducible synthetic cases
```

Includes the seeded generator, exactly 40 initial cases, and schema
documentation.

### 7. Experiment runner

```text
feat(experiment): compare agent policies
```

Includes running baseline, Policy A, and Policy B on every case and saving
machine-readable results.

### 8. Metrics

```text
feat(metrics): calculate risk decision metrics
```

Includes confusion matrices, fraud precision/recall, action rates, review
rate, total cost, average cost, and calibration where appropriate.

### 9. Feedback loop

```text
feat(agent): add verification feedback updates
```

Includes simulated callback evidence, posterior updates, and separate initial
and post-feedback decisions.

### 10. Failure analysis

```text
feat(analysis): generate decision failure report
```

Includes selection of at least five actual incorrect or high-cost decisions
from executed experiment output.

### 11. Automated tests

```text
test: cover agent and experiment behavior
```

Includes belief, action, threshold, hidden-label, feedback, persistence, and
metric tests.

### 12. Figures and results

```text
feat(reporting): generate experiment figures
```

Includes result tables and figures generated only from actual experiment
output.

### 13. Documentation

```text
docs: document reproducible project workflow
```

Includes README, research-file, discussion-record, review-record, and honest
AI-use and human-contribution statements.

### 14. Preprint

```text
docs(paper): add IJCAI-style course preprint
```

Includes LaTeX, bibliography placeholders/checklist, figures, limitations,
and explicit author-kit verification status.

### 15. Social drafts

```text
docs(social): add evidence-backed post templates
```

Includes LinkedIn and X drafts with unresolved claims marked as TODO until
actual results and discussions exist.

## Commit rules

- Run tests before committing implementation changes.
- Never include generated results unless the generating command is recorded.
- Keep simulated assumptions separate from verified evidence.
- Update `PROJECT_CONTEXT.md` when a milestone or decision changes.
- Do not create a commit claiming results before the experiment has run.
