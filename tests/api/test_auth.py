"""Authentication endpoint, including its HTTP 200 + reason quirk."""

from __future__ import annotations

import pytest

from qa_portfolio.api import BookingApi

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
def test_issues_a_token_for_valid_credentials(booking_api: BookingApi) -> None:
    token = booking_api.authenticate()

    assert token
    assert len(token) > 5


def test_rejects_invalid_credentials_without_issuing_a_token(booking_api: BookingApi) -> None:
    response = booking_api.authenticate_response("invalid-user", "invalid-password")

    # Restful Booker signals auth failure with HTTP 200 and a reason body.
    assert response.status_code == 200

    body = booking_api.parse_auth_failure(response)
    assert body.reason == "Bad credentials"
