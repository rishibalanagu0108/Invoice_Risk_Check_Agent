"""Calculate metrics from generated experiment results."""

import json
from pathlib import Path

from invoice_agent.metrics import (
    calculate_all_metrics,
    save_metrics,
    save_metrics_summary_csv,
)


if __name__ == "__main__":
    results_path = Path("results/experiment_results.json")
    results = json.loads(results_path.read_text(encoding="utf-8"))
    metrics = calculate_all_metrics(results)
    save_metrics(metrics, "results/metrics.json")
    save_metrics_summary_csv(metrics, "results/metrics_summary.csv")
    print("Saved metrics to results/")
