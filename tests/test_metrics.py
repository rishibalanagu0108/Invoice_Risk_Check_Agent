from invoice_agent.experiment import run_experiment
from invoice_agent.metrics import (
    calculate_all_metrics,
    calculate_policy_metrics,
    confusion_matrix,
)


def test_confusion_matrix_counts_state_action_pairs() -> None:
    results = [
        {"true_state": "FRAUD", "action": "HOLD"},
        {"true_state": "FRAUD", "action": "APPROVE"},
        {"true_state": "LEGITIMATE", "action": "APPROVE"},
    ]

    matrix = confusion_matrix(results)

    assert matrix["FRAUD"]["HOLD"] == 1
    assert matrix["FRAUD"]["APPROVE"] == 1
    assert matrix["LEGITIMATE"]["APPROVE"] == 1


def test_metrics_calculate_from_experiment_results(tmp_path) -> None:
    results = run_experiment(output_dir=tmp_path)

    metrics = calculate_all_metrics(results)
    assert set(metrics["policies"]) == {"baseline", "policy_a", "policy_b"}
    assert all(
        policy_metrics["case_count"] == 40
        for policy_metrics in metrics["policies"].values()
    )


def test_fraud_precision_and_recall_definition() -> None:
    results = [
        {
            "policy": "test",
            "true_state": "FRAUD",
            "action": "HOLD",
            "human_review_required": True,
            "actual_cost": 5,
            "expected_cost": 5,
        },
        {
            "policy": "test",
            "true_state": "FRAUD",
            "action": "APPROVE",
            "human_review_required": False,
            "actual_cost": 100,
            "expected_cost": 100,
        },
        {
            "policy": "test",
            "true_state": "LEGITIMATE",
            "action": "ESCALATE",
            "human_review_required": True,
            "actual_cost": 10,
            "expected_cost": 10,
        },
        {
            "policy": "test",
            "true_state": "ERROR",
            "action": "VERIFY",
            "human_review_required": False,
            "actual_cost": 8,
            "expected_cost": 8,
        },
    ]

    metrics = calculate_policy_metrics(results, "test")

    assert metrics["fraud_precision"] == 0.5
    assert metrics["fraud_recall"] == 0.5
