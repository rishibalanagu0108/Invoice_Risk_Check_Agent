import json

from invoice_agent.analysis import identify_failures, save_failure_report
from invoice_agent.experiment import run_experiment
from invoice_agent.beliefs import load_assumptions


def test_failure_analysis_selects_at_least_five_actual_failures(tmp_path) -> None:
    results = run_experiment(output_dir=tmp_path)
    config = load_assumptions("config/simulation_assumptions.json")

    failures = identify_failures(results, config)

    assert len(failures) >= 5
    assert all(failure["actual_cost"] > 0 for failure in failures)
    assert all("possible_improvement" in failure for failure in failures)


def test_failure_report_is_written_from_results(tmp_path) -> None:
    results_dir = tmp_path / "results"
    run_experiment(output_dir=results_dir)

    failures = save_failure_report(
        results_path=results_dir / "experiment_results.json",
        output_dir=results_dir,
    )

    report = json.loads((results_dir / "failure_analysis.json").read_text())
    assert len(report["failures"]) == len(failures)
    assert (results_dir / "failure_analysis.md").exists()
