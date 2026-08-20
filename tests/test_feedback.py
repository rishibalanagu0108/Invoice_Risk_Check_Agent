from invoice_agent.beliefs import calculate_beliefs, load_assumptions
from invoice_agent.data_generation import generate_cases
from invoice_agent.feedback import (
    apply_callback_result,
    run_feedback_experiment,
)
from invoice_agent.models import HiddenState
from invoice_agent.policies import policy_b_action


def test_callback_result_updates_case_without_changing_hidden_state() -> None:
    case = generate_cases()[0]
    updated = apply_callback_result(case, callback_verified=False)

    assert updated.callback_verified is False
    assert updated.true_state == case.true_state
    assert "true_state" not in updated.observation()


def test_successful_verification_can_enable_approval() -> None:
    config = load_assumptions("config/simulation_assumptions.json")
    case = next(case for case in generate_cases() if case.case_id == "case-008")
    before = calculate_beliefs(case.observation(), config)
    updated = apply_callback_result(case, True)
    after = calculate_beliefs(updated.observation(), config)

    assert policy_b_action(before, config, case.observation()).value == "VERIFY"
    assert policy_b_action(after, config, updated.observation()).value == "APPROVE"
    assert updated.duplicate_invoice_signal is False


def test_negative_callback_increases_fraud_belief_for_suspicious_case() -> None:
    config = load_assumptions("config/simulation_assumptions.json")
    case = next(
        case
        for case in generate_cases()
        if case.bank_account_changed and case.true_state is HiddenState.FRAUD
    )
    before = calculate_beliefs(case.observation(), config)
    after = calculate_beliefs(
        apply_callback_result(case, False).observation(), config
    )

    assert after[HiddenState.FRAUD] > before[HiddenState.FRAUD]


def test_feedback_experiment_keeps_initial_and_post_decisions(tmp_path) -> None:
    records = run_feedback_experiment(output_path=tmp_path / "feedback.json")

    assert records
    assert all("initial" in record for record in records)
    assert all("post_feedback" in record for record in records)
    assert all("true_state" not in record["initial"]["evidence"] for record in records)
    assert all(
        record["initial"]["action"] == "VERIFY" for record in records
    )
