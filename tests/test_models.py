import pytest

from invoice_agent.models import Action, HiddenState, InvoiceCase


def make_case(**overrides: object) -> InvoiceCase:
    values: dict[str, object] = {
        "case_id": "case-001",
        "vendor_id": "vendor-001",
        "vendor_age_days": 800,
        "existing_vendor": True,
        "invoice_amount": 1000.0,
        "historical_average_amount": 900.0,
        "bank_account_changed": False,
        "bank_change_age_days": None,
        "email_domain_changed": False,
        "lookalike_domain_signal": False,
        "invoice_number_pattern_valid": True,
        "duplicate_invoice_signal": False,
        "purchase_order_match": True,
        "payment_terms_match": True,
        "unusual_urgency": False,
        "location_changed": False,
        "vendor_contact_verified": True,
        "callback_verified": None,
        "supporting_documents_available": True,
        "true_state": HiddenState.LEGITIMATE,
    }
    values.update(overrides)
    return InvoiceCase(**values)  # type: ignore[arg-type]


def test_actions_and_hidden_states_are_restricted() -> None:
    assert set(Action) == {
        Action.APPROVE,
        Action.VERIFY,
        Action.HOLD,
        Action.ESCALATE,
    }
    assert set(HiddenState) == {
        HiddenState.LEGITIMATE,
        HiddenState.ERROR,
        HiddenState.FRAUD,
    }


def test_observation_excludes_true_state() -> None:
    case = make_case()

    assert "true_state" not in case.observation()
    assert case.to_dict()["true_state"] == HiddenState.LEGITIMATE


def test_amount_deviation_ratio() -> None:
    assert make_case(invoice_amount=1800.0).amount_deviation_ratio == 2.0


def test_bank_change_age_requires_bank_change() -> None:
    with pytest.raises(ValueError, match="bank_change_age_days"):
        make_case(bank_change_age_days=3)


def test_negative_amount_is_rejected() -> None:
    with pytest.raises(ValueError, match="invoice_amount"):
        make_case(invoice_amount=-1.0)
