"""Run the simulated verification feedback experiment."""

from invoice_agent.feedback import run_feedback_experiment


if __name__ == "__main__":
    records = run_feedback_experiment()
    print(f"Saved {len(records)} feedback records to results/feedback_results.json")
