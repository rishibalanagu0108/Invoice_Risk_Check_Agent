from app import action_label
from invoice_agent.models import Action


def test_ui_action_labels_use_domain_actions() -> None:
    assert action_label(Action.APPROVE) == "APPROVE"
    assert action_label(Action.VERIFY) == "VERIFY"
    assert action_label(Action.HOLD) == "HOLD"
    assert action_label(Action.ESCALATE) == "ESCALATE"
