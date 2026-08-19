"""Core domain types for invoice and payment-risk decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class HiddenState(StrEnum):
    """The actual state of a case, hidden during prediction."""

    LEGITIMATE = "LEGITIMATE"
    ERROR = "ERROR"
    FRAUD = "FRAUD"


class Action(StrEnum):
    """Actions available to the decision agent."""

    APPROVE = "APPROVE"
    VERIFY = "VERIFY"
    HOLD = "HOLD"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True, slots=True)
class InvoiceCase:
    """One invoice/payment case used by the agent and evaluator.

    ``true_state`` is an evaluation-only label. Prediction code must consume
    :meth:`observation`, which deliberately excludes it.
    """

    case_id: str
    vendor_id: str
    vendor_age_days: int
    existing_vendor: bool
    invoice_amount: float
    historical_average_amount: float
    bank_account_changed: bool
    bank_change_age_days: int | None
    email_domain_changed: bool
    lookalike_domain_signal: bool
    invoice_number_pattern_valid: bool
    duplicate_invoice_signal: bool
    purchase_order_match: bool
    payment_terms_match: bool
    unusual_urgency: bool
    location_changed: bool
    vendor_contact_verified: bool
    callback_verified: bool | None
    supporting_documents_available: bool
    true_state: HiddenState | None = None

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("case_id must not be empty")
        if not self.vendor_id.strip():
            raise ValueError("vendor_id must not be empty")
        if self.vendor_age_days < 0:
            raise ValueError("vendor_age_days must be non-negative")
        if self.invoice_amount < 0:
            raise ValueError("invoice_amount must be non-negative")
        if self.historical_average_amount <= 0:
            raise ValueError("historical_average_amount must be positive")
        if self.bank_change_age_days is not None and self.bank_change_age_days < 0:
            raise ValueError("bank_change_age_days must be non-negative")
        if not self.bank_account_changed and self.bank_change_age_days is not None:
            raise ValueError(
                "bank_change_age_days requires bank_account_changed=True"
            )

    @property
    def amount_deviation_ratio(self) -> float:
        """Return invoice amount divided by its historical average."""

        return self.invoice_amount / self.historical_average_amount

    def observation(self) -> dict[str, Any]:
        """Return prediction-time data without the hidden evaluation label."""

        data = asdict(self)
        data.pop("true_state")
        return data

    def to_dict(self) -> dict[str, Any]:
        """Return the complete case, including its evaluation label."""

        return asdict(self)
