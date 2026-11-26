"""Booking lifecycle: create, read, filter, update and delete.

The `booking_factory` fixture deletes every booking it creates, so these tests
are independent and safe to run in parallel.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from qa_portfolio.api import BookingApi
from qa_portfolio.models.booking import Booking, CreatedBooking

pytestmark = [pytest.mark.api, pytest.mark.regression]

BookingFactory = Callable[..., CreatedBooking]


@pytest.mark.smoke
def test_creates_a_booking_and_reads_it_back(
    booking_factory: BookingFactory, booking_api: BookingApi
) -> None:
    created = booking_factory()

    assert created.bookingid > 0

    fetched = booking_api.get(created.bookingid)
    assert fetched == created.booking


def test_filters_bookings_by_customer_name(
    booking_factory: BookingFactory, booking_api: BookingApi
) -> None:
    created = booking_factory({"firstname": "Manikandan", "lastname": "Kandasamy"})

    ids = booking_api.list_ids(firstname="Manikandan", lastname="Kandasamy")

    assert created.bookingid in ids


def test_replaces_a_booking_with_a_full_update(
    booking_factory: BookingFactory, booking_api: BookingApi
) -> None:
    created = booking_factory()

    updated = created.booking.model_copy(
        update={
            "firstname": "Updated",
            "totalprice": created.booking.totalprice + 25,
            "depositpaid": not created.booking.depositpaid,
        }
    )

    response = booking_api.replace(created.bookingid, updated)
    assert response.status_code == 200

    persisted = booking_api.get(created.bookingid)
    assert persisted == updated


def test_applies_a_partial_update(booking_factory: BookingFactory, booking_api: BookingApi) -> None:
    created = booking_factory()

    response = booking_api.partial_update(
        created.bookingid, {"additionalneeds": "Airport transfer"}
    )
    assert response.status_code == 200

    persisted: Booking = booking_api.get(created.bookingid)
    assert persisted.firstname == created.booking.firstname
    assert persisted.additionalneeds == "Airport transfer"


def test_deletes_a_booking_and_then_reports_it_missing(
    booking_factory: BookingFactory, booking_api: BookingApi
) -> None:
    created = booking_factory()

    deleted = booking_api.delete(created.bookingid)
    assert deleted.status_code == 201

    assert booking_api.get_response(created.bookingid).status_code == 404
