"""Generate failure analysis from the executed experiment."""

from invoice_agent.analysis import save_failure_report


if __name__ == "__main__":
    failures = save_failure_report()
    print(f"Saved {len(failures)} failure records to results/")
