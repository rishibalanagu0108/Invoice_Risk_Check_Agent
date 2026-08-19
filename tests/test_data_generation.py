from invoice_agent.data_generation import generate_cases, load_cases_csv, save_cases_csv
from invoice_agent.models import HiddenState


def test_generator_creates_exactly_40_cases() -> None:
    cases = generate_cases()

    assert len(cases) == 40
    assert {case.true_state for case in cases} == set(HiddenState)


def test_generator_is_reproducible() -> None:
    first = generate_cases(seed=42)
    second = generate_cases(seed=42)

    assert [case.to_dict() for case in first] == [case.to_dict() for case in second]


def test_generator_produces_required_state_counts() -> None:
    cases = generate_cases()
    counts = {state: sum(case.true_state is state for case in cases) for state in HiddenState}

    assert counts == {
        HiddenState.LEGITIMATE: 16,
        HiddenState.ERROR: 12,
        HiddenState.FRAUD: 12,
    }


def test_observation_does_not_include_hidden_state() -> None:
    assert all("true_state" not in case.observation() for case in generate_cases())


def test_csv_round_trip_preserves_cases(tmp_path) -> None:
    original = generate_cases()
    path = tmp_path / "cases.csv"

    save_cases_csv(original, path)
    loaded = load_cases_csv(path)

    assert [case.to_dict() for case in loaded] == [
        case.to_dict() for case in original
    ]
