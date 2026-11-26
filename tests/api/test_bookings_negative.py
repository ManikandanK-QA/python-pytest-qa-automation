"""Negative API paths: missing resources, missing auth and invalid payloads."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from qa_portfolio.api import ApiClient, BookingApi
from qa_portfolio.models.booking import CreatedBooking

pytestmark = [pytest.mark.api, pytest.mark.regression]

BookingFactory = Callable[..., CreatedBooking]


def test_returns_404_for_an_unknown_booking_id(booking_api: BookingApi) -> None:
    assert booking_api.get_response(9_999_999).status_code == 404


def test_rejects_a_full_update_without_a_token(
    api_client: ApiClient, booking_factory: BookingFactory
) -> None:
    created = booking_factory()

    response = api_client.put(f"/booking/{created.bookingid}", json=created.booking.model_dump())

    assert response.status_code == 403


def test_rejects_a_delete_without_a_token(
    api_client: ApiClient, booking_factory: BookingFactory
) -> None:
    created = booking_factory()

    response = api_client.delete(f"/booking/{created.bookingid}")

    assert response.status_code == 403


def test_rejects_a_create_payload_with_missing_required_fields(api_client: ApiClient) -> None:
    response = api_client.post("/booking", json={"firstname": "Incomplete"})

    assert response.status_code == 500
