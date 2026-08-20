"""Reproducible synthetic invoice-case generation."""

from __future__ import annotations

import csv
import random
from dataclasses import replace
from pathlib import Path
from typing import Iterable

from .models import HiddenState, InvoiceCase


CASE_COUNT = 40
DEFAULT_SEED = 42


def _base_case(case_id: str, rng: random.Random) -> InvoiceCase:
    average = float(rng.choice([500, 900, 1500, 3000, 7500]))
    return InvoiceCase(
        case_id=case_id,
        vendor_id=f"vendor-{rng.randint(1, 12):03d}",
        vendor_age_days=rng.choice([30, 120, 365, 800, 2400]),
        existing_vendor=True,
        invoice_amount=average,
        historical_average_amount=average,
        bank_account_changed=False,
        bank_change_age_days=None,
        email_domain_changed=False,
        lookalike_domain_signal=False,
        invoice_number_pattern_valid=True,
        duplicate_invoice_signal=False,
        purchase_order_match=True,
        payment_terms_match=True,
        unusual_urgency=False,
        location_changed=False,
        vendor_contact_verified=True,
        callback_verified=None,
        supporting_documents_available=True,
    )


def _case_for_state(
    case_id: str, state: HiddenState, index: int, rng: random.Random
) -> InvoiceCase:
    case = _base_case(case_id, rng)

    if state is HiddenState.LEGITIMATE:
        amount_multiplier = rng.choice([0.9, 1.0, 1.1, 1.3])
        case = replace(
            case,
            invoice_amount=round(case.historical_average_amount * amount_multiplier, 2),
            callback_verified=True if index % 5 == 0 else None,
            true_state=state,
        )
        if index % 4 == 0:
            case = replace(case, bank_account_changed=True, bank_change_age_days=90)
        # Showcase case: verification can resolve a suspected duplicate while
        # the legitimate bank-account change remains independently confirmed.
        if index == 8:
            case = replace(case, duplicate_invoice_signal=True)

    elif state is HiddenState.ERROR:
        scenarios = [
            {"duplicate_invoice_signal": True},
            {"purchase_order_match": False},
            {"payment_terms_match": False, "unusual_urgency": True},
            {"invoice_number_pattern_valid": False},
            {"location_changed": True},
        ]
        changes = scenarios[index % len(scenarios)]
        amount_multiplier = rng.choice([0.7, 1.4, 1.8, 2.2])
        case = replace(
            case,
            invoice_amount=round(case.historical_average_amount * amount_multiplier, 2),
            vendor_contact_verified=False if index % 3 == 0 else True,
            true_state=state,
            **changes,
        )

    else:
        scenarios = [
            {
                "bank_account_changed": True,
                "bank_change_age_days": 1,
                "email_domain_changed": True,
            },
            {"lookalike_domain_signal": True, "unusual_urgency": True},
            {"duplicate_invoice_signal": True, "purchase_order_match": False},
            {"bank_account_changed": True, "bank_change_age_days": 3},
            {"location_changed": True, "payment_terms_match": False},
        ]
        changes = scenarios[index % len(scenarios)]
        amount_multiplier = rng.choice([2.0, 3.0, 5.0, 8.0])
        case = replace(
            case,
            invoice_amount=round(case.historical_average_amount * amount_multiplier, 2),
            vendor_contact_verified=False,
            supporting_documents_available=False,
            true_state=state,
            **changes,
        )

    return case


def generate_cases(count: int = CASE_COUNT, seed: int = DEFAULT_SEED) -> list[InvoiceCase]:
    """Generate a deterministic, varied collection of labeled synthetic cases."""

    if count != CASE_COUNT:
        raise ValueError(f"Version 1 requires exactly {CASE_COUNT} cases")

    rng = random.Random(seed)
    states = (
        [HiddenState.LEGITIMATE] * 16
        + [HiddenState.ERROR] * 12
        + [HiddenState.FRAUD] * 12
    )
    rng.shuffle(states)
    return [
        _case_for_state(f"case-{index:03d}", state, index, rng)
        for index, state in enumerate(states, start=1)
    ]


CASE_FIELDS = [
    "case_id",
    "vendor_id",
    "vendor_age_days",
    "existing_vendor",
    "invoice_amount",
    "historical_average_amount",
    "bank_account_changed",
    "bank_change_age_days",
    "email_domain_changed",
    "lookalike_domain_signal",
    "invoice_number_pattern_valid",
    "duplicate_invoice_signal",
    "purchase_order_match",
    "payment_terms_match",
    "unusual_urgency",
    "location_changed",
    "vendor_contact_verified",
    "callback_verified",
    "supporting_documents_available",
    "true_state",
]


def cases_to_rows(cases: Iterable[InvoiceCase]) -> list[dict[str, str]]:
    """Serialize cases into CSV-compatible string rows."""

    return [
        {
            **{
                key: str(value).lower() if isinstance(value, bool) else str(value)
                for key, value in case.to_dict().items()
                if key != "true_state"
            },
            "bank_change_age_days": (
                "" if case.bank_change_age_days is None else str(case.bank_change_age_days)
            ),
            "callback_verified": (
                "" if case.callback_verified is None else str(case.callback_verified).lower()
            ),
            "true_state": case.true_state.value if case.true_state else "",
        }
        for case in cases
    ]


def save_cases_csv(cases: Iterable[InvoiceCase], path: str | Path) -> None:
    """Write cases to a typed, human-readable CSV file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CASE_FIELDS)
        writer.writeheader()
        writer.writerows(cases_to_rows(cases))


def _parse_bool(value: str, field: str) -> bool:
    if value not in {"true", "false"}:
        raise ValueError(f"{field} must be true or false")
    return value == "true"


def _parse_optional_bool(value: str, field: str) -> bool | None:
    if value == "":
        return None
    return _parse_bool(value, field)


def load_cases_csv(path: str | Path) -> list[InvoiceCase]:
    """Load and type-convert cases from the canonical CSV dataset."""

    with Path(path).open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != CASE_FIELDS:
            raise ValueError("CSV columns do not match the InvoiceCase schema")
        cases = []
        for row in reader:
            cases.append(
                InvoiceCase(
                    case_id=row["case_id"],
                    vendor_id=row["vendor_id"],
                    vendor_age_days=int(row["vendor_age_days"]),
                    existing_vendor=_parse_bool(row["existing_vendor"], "existing_vendor"),
                    invoice_amount=float(row["invoice_amount"]),
                    historical_average_amount=float(row["historical_average_amount"]),
                    bank_account_changed=_parse_bool(
                        row["bank_account_changed"], "bank_account_changed"
                    ),
                    bank_change_age_days=(
                        None
                        if row["bank_change_age_days"] == ""
                        else int(row["bank_change_age_days"])
                    ),
                    email_domain_changed=_parse_bool(
                        row["email_domain_changed"], "email_domain_changed"
                    ),
                    lookalike_domain_signal=_parse_bool(
                        row["lookalike_domain_signal"], "lookalike_domain_signal"
                    ),
                    invoice_number_pattern_valid=_parse_bool(
                        row["invoice_number_pattern_valid"],
                        "invoice_number_pattern_valid",
                    ),
                    duplicate_invoice_signal=_parse_bool(
                        row["duplicate_invoice_signal"], "duplicate_invoice_signal"
                    ),
                    purchase_order_match=_parse_bool(
                        row["purchase_order_match"], "purchase_order_match"
                    ),
                    payment_terms_match=_parse_bool(
                        row["payment_terms_match"], "payment_terms_match"
                    ),
                    unusual_urgency=_parse_bool(row["unusual_urgency"], "unusual_urgency"),
                    location_changed=_parse_bool(row["location_changed"], "location_changed"),
                    vendor_contact_verified=_parse_bool(
                        row["vendor_contact_verified"], "vendor_contact_verified"
                    ),
                    callback_verified=_parse_optional_bool(
                        row["callback_verified"], "callback_verified"
                    ),
                    supporting_documents_available=_parse_bool(
                        row["supporting_documents_available"],
                        "supporting_documents_available",
                    ),
                    true_state=(
                        None
                        if row["true_state"] == ""
                        else HiddenState(row["true_state"])
                    ),
                )
            )
        return cases


if __name__ == "__main__":
    save_cases_csv(generate_cases(), Path("data/cases.csv"))
