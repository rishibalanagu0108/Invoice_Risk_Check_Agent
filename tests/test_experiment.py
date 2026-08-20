import json

from invoice_agent.experiment import run_experiment


def test_experiment_runs_all_policies(tmp_path) -> None:
    results = run_experiment(output_dir=tmp_path)

    assert len(results) == 120
    assert {result["policy"] for result in results} == {
        "baseline",
        "policy_a",
        "policy_b",
    }
    assert (tmp_path / "experiment_results.json").exists()
    assert (tmp_path / "experiment_summary.csv").exists()


def test_hidden_state_is_not_in_prediction_evidence(tmp_path) -> None:
    results = run_experiment(output_dir=tmp_path)

    assert all("true_state" not in result["evidence"] for result in results)


def test_saved_json_is_readable(tmp_path) -> None:
    run_experiment(output_dir=tmp_path)

    saved = json.loads((tmp_path / "experiment_results.json").read_text())
    assert len(saved) == 120
    assert all("action" in result for result in saved)
