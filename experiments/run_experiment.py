"""Run the Version-1 invoice-risk experiment from the repository root."""

from invoice_agent.experiment import run_experiment


if __name__ == "__main__":
    results = run_experiment()
    print(f"Saved {len(results)} decision records to results/")
