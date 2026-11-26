"""Synthetic data factories.

Tests pass explicit overrides when a value is part of the assertion and let the
factory supply the rest, so payloads stay realistic without shared mutable
fixtures.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TypedDict

from faker import Faker

from qa_portfolio.models.booking import Booking, BookingDates

_fake = Faker()


class BookingOverrides(TypedDict, total=False):
    """Optional field-level overrides for `build_booking`."""

    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates | dict[str, str]
    additionalneeds: str | None


def build_booking(overrides: BookingOverrides | None = None) -> Booking:
    """Return a valid booking payload with synthetic values."""

    checkin = _fake.date_between(start_date="+1d", end_date="+30d")
    checkout = checkin + timedelta(days=_fake.random_int(min=1, max=7))

    payload: dict[str, object] = {
        "firstname": _fake.first_name(),
        "lastname": _fake.last_name(),
        "totalprice": _fake.random_int(min=50, max=500),
        "depositpaid": _fake.boolean(),
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": _fake.random_element(
            elements=("Breakfast", "Late checkout", "Extra pillows")
        ),
    }
    payload.update(overrides or {})
    return Booking.model_validate(payload)
