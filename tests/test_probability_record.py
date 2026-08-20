from pathlib import Path

from invoice_agent.beliefs import calculate_beliefs, load_assumptions
from invoice_agent.data_generation import load_cases_csv
from invoice_agent.policies import policy_b_action


def test_probability_record_case_has_normalized_prior_and_changed_action() -> None:
    config = load_assumptions("config/simulation_assumptions.json")
    case = next(case for case in load_cases_csv("data/cases.csv") if case.case_id == "case-006")
    initial = calculate_beliefs(case.observation(), config)
    updated_case = next(
        case for case in load_cases_csv("data/cases.csv") if case.case_id == "case-006"
    )
    from dataclasses import replace

    posterior = calculate_beliefs(
        replace(updated_case, callback_verified=False).observation(), config
    )

    assert sum(initial.values()) == 1.0
    assert sum(posterior.values()) == 1.0
    assert policy_b_action(initial, config, case.observation()).value == "VERIFY"
    assert policy_b_action(
        posterior, config, replace(updated_case, callback_verified=False).observation()
    ).value == "HOLD"


def test_probability_record_file_exists() -> None:
    assert Path("decisions/probability-decision-record.md").exists()
