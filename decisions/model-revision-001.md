# Model Revision 001 — Failure-Driven Changes

Status: Executed and re-evaluated

## Trigger

The first executed experiment showed that Policy A and Policy B approved most
cases and both had zero fraud recall. Failure analysis found fraud cases with
duplicate signals, large amount deviations, missing documents, and unverified
contacts receiving very low fraud beliefs.

## Changes

1. Added derived prediction-time evidence:
   - `amount_unusual`
   - `supporting_documents_missing`
   - `high_risk_signal_count`
   - `multiple_high_risk_signals`
2. Revised duplicate-invoice likelihood assumptions so duplicate evidence can
   support both error and fraud explanations.
3. Added configurable likelihoods for the new evidence.
4. Added a safety gate preventing Policy A and Policy B from directly approving
   duplicate invoices or cases with multiple high-risk signals.
5. Passed the complete observation into the policies so the safety gate does
   not use the hidden label.

## Leakage check

The hidden `true_state` is not used by the belief model or policy. It is used
only by the synthetic callback oracle and the evaluator after prediction.

## Re-evaluation requirement

The experiment, metrics, and failure analysis must be regenerated after this
revision. The new results remain simulated and must not be presented as
real-world evidence.
