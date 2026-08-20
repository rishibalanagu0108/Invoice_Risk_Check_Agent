# Research File

Status: preparation file; external sources and human discussions require manual
verification.

## Problem statement

The agent observes an invoice, vendor information, payment details, and
available history. It must approve, verify, hold, or escalate the payment
because the legitimacy and risk of the payment are not fully known.

## Project objective

Build a small, testable agent that represents hidden states, beliefs, actions,
costs, policy, feedback, and belief updates for invoice/payment risk decisions.

## Current assumptions

- Data is synthetic and generated with a fixed seed.
- Priors, likelihoods, thresholds, and costs are configurable assumptions.
- The true state is hidden from the agent during prediction.
- An independent callback can produce new evidence in simulation.
- The current likelihood update treats evidence items as conditionally
  independent.

## Technical terms

- Hidden state: the actual condition not directly observed at decision time.
- Prior: belief before considering the observed evidence.
- Likelihood: modeled compatibility of evidence with a hidden state.
- Posterior: updated belief after evidence.
- Expected cost: probability-weighted consequence of an action.
- Calibration: whether predicted probabilities match observed frequencies.
- False positive: protective intervention on a non-fraud case.
- False negative: failure to apply a protective action to fraud.

## Search queries

TODO: Add the exact queries used for external research, dates searched, and
search engines or databases.

## Verified Reddit communities

TODO: Add only communities that were actually verified, with links and dates.

## Relevant X accounts

TODO: Add only accounts that were actually verified as relevant, with links and
dates.

## Papers, articles, repositories, and datasets

TODO: Add only sources that were located, read, and manually verified.

## Research questions

1. Which invoice evidence signals are useful for distinguishing error from
   fraud?
2. How should review capacity affect action costs and thresholds?
3. How sensitive are decisions to prior and likelihood assumptions?
4. How should verification evidence be calibrated in a production setting?
5. What human-control requirements are necessary before payment automation?

## AI prompts used

TODO: Record prompts used for planning, coding, critique, literature
preparation, or review assistance.

## AI mistakes/issues

The first experiment showed that the belief-based policies approved too many
fraud cases. Failure analysis led to Model Revision 001. Record future issues
here with the command, evidence, and correction.

## Claims requiring evidence

- Real-world fraud prevalence or likelihoods.
- Effectiveness of any feature in deployed payment systems.
- Claims about industry practice or regulatory requirements.
- Claims about novelty or superiority over existing methods.
- Any external account, community, paper, or dataset.

## Open questions

- Which likelihood assumptions can be supported by verified sources?
- How should correlated evidence be modeled beyond Version 1?
- What is the appropriate human escalation policy?
- How should privacy and data retention be handled with real invoices?
