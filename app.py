"""Streamlit showcase for the invoice/payment risk agent."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import streamlit as st

from invoice_agent.beliefs import calculate_beliefs, load_assumptions
from invoice_agent.data_generation import load_cases_csv
from invoice_agent.feedback import apply_callback_result
from invoice_agent.models import Action
from invoice_agent.policies import (
    baseline_action,
    expected_costs,
    policy_a_action,
    policy_b_action,
)


ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config" / "simulation_assumptions.json"
CASES_PATH = ROOT / "data" / "cases.csv"


@st.cache_data
def get_config() -> dict:
    return load_assumptions(CONFIG_PATH)


@st.cache_data
def get_cases():
    return load_cases_csv(CASES_PATH)


def choose_action(case, evidence, beliefs, config, policy_name):
    if policy_name == "Baseline":
        return baseline_action(case)
    if policy_name == "Policy A — Efficiency":
        return policy_a_action(beliefs, config, evidence)
    return policy_b_action(beliefs, config, evidence)


def action_label(action: Action) -> str:
    labels = {
        Action.APPROVE: "APPROVE",
        Action.VERIFY: "VERIFY",
        Action.HOLD: "HOLD",
        Action.ESCALATE: "ESCALATE",
    }
    return labels[action]


def render_decision(case, config, policy_name):
    evidence = case.observation()
    beliefs = calculate_beliefs(evidence, config)
    action = choose_action(case, evidence, beliefs, config, policy_name)
    costs = expected_costs(beliefs, config["costs"])

    st.subheader("Decision")
    metric_columns = st.columns(4)
    for column, state in zip(metric_columns, beliefs):
        column.metric(state.value, f"{beliefs[state]:.2%}")

    st.success(f"Selected action: {action_label(action)}")
    st.caption(
        "The action is produced by the existing agent logic. Probabilities and "
        "costs are configurable simulation assumptions."
    )

    st.subheader("Expected action costs")
    st.dataframe(
        [
            {"Action": action.value, "Expected cost": round(cost, 4)}
            for action, cost in costs.items()
        ],
        hide_index=True,
        use_container_width=True,
    )

    with st.expander("Evidence used by the agent", expanded=True):
        st.dataframe(
            [
                {"Feature": key, "Value": value}
                for key, value in evidence.items()
            ],
            hide_index=True,
            use_container_width=True,
        )

    if action is Action.VERIFY:
        st.subheader("Simulated verification feedback")
        callback = st.selectbox(
            "Independent callback result",
            options=[True, False],
            format_func=lambda value: "Vendor confirmed" if value else "Vendor denied",
        )
        if st.button("Apply callback and decide again"):
            updated_case = apply_callback_result(case, callback)
            updated_evidence = updated_case.observation()
            updated_beliefs = calculate_beliefs(updated_evidence, config)
            updated_action = choose_action(
                updated_case,
                updated_evidence,
                updated_beliefs,
                config,
                policy_name,
            )
            st.divider()
            st.subheader("Post-feedback decision")
            st.write(
                f"Beliefs after callback: Legitimate **{updated_beliefs[next(state for state in updated_beliefs if state.value == 'LEGITIMATE')]:.2%}**, "
                f"Error **{updated_beliefs[next(state for state in updated_beliefs if state.value == 'ERROR')]:.2%}**, "
                f"Fraud **{updated_beliefs[next(state for state in updated_beliefs if state.value == 'FRAUD')]:.2%}**"
            )
            st.warning(f"Updated action: {action_label(updated_action)}")


def render_metrics() -> None:
    metrics_path = ROOT / "results" / "metrics_summary.csv"
    failures_path = ROOT / "results" / "failure_analysis.md"
    if metrics_path.exists():
        import csv

        with metrics_path.open(encoding="utf-8", newline="") as file:
            st.dataframe(list(csv.DictReader(file)), hide_index=True, use_container_width=True)
    else:
        st.info("Run the experiment and metrics commands to populate this tab.")
    if failures_path.exists():
        st.subheader("Failure analysis")
        st.markdown(failures_path.read_text(encoding="utf-8"))


def main() -> None:
    st.set_page_config(page_title="Invoice Risk Agent", page_icon="🧾", layout="wide")
    config = get_config()
    cases = get_cases()

    st.title("Invoice / Payment Risk Agent")
    st.caption(
        "A transparent showcase for a synthetic, cost-sensitive payment-risk experiment."
    )

    with st.sidebar:
        st.header("Decision controls")
        selected_case_id = st.selectbox("Case", [case.case_id for case in cases])
        selected_policy = st.radio(
            "Decision system",
            ["Baseline", "Policy A — Efficiency", "Policy B — Risk-sensitive"],
        )
        show_label = st.checkbox("Show evaluator-only hidden state", value=False)
        st.divider()
        st.info(
            "The agent does not use the hidden state during prediction. "
            "All cases and probabilities are synthetic."
        )

    selected_case = next(case for case in cases if case.case_id == selected_case_id)
    if show_label:
        st.warning(f"Evaluator-only label: {selected_case.true_state.value}")

    decision_tab, data_tab, metrics_tab = st.tabs(
        ["Decision", "Dataset", "Results"]
    )
    with decision_tab:
        render_decision(selected_case, config, selected_policy)
    with data_tab:
        st.subheader("Synthetic dataset")
        st.write(f"{len(cases)} cases generated with a fixed seed.")
        st.dataframe(
            [case.to_dict() for case in cases],
            hide_index=True,
            use_container_width=True,
        )
    with metrics_tab:
        render_metrics()


if __name__ == "__main__":
    main()
