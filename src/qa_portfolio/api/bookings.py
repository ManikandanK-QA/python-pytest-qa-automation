"""Endpoint object for the Restful Booker API.

Responsibilities kept here: paths, payload shapes, token handling and response
contracts. Assertions stay in the specs.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from qa_portfolio.api.client import ApiClient
from qa_portfolio.api.errors import ApiRequestError
from qa_portfolio.models.booking import (
    AuthFailure,
    AuthToken,
    Booking,
    BookingId,
    CreatedBooking,
)


@dataclass(frozen=True, slots=True)
class Credentials:
    """Username and password for the Booker auth endpoint."""

    username: str
    password: str


class BookingApi:
    """Booking operations with a lazily acquired auth token."""

    def __init__(self, client: ApiClient, credentials: Credentials) -> None:
        self.client = client
        self._credentials = credentials
        self._token: str | None = None

    # --- Authentication -------------------------------------------------

    def authenticate(self) -> str:
        """Return a cached token, requesting one on first use."""

        if self._token is None:
            response = self.client.post(
                "/auth",
                json={
                    "username": self._credentials.username,
                    "password": self._credentials.password,
                },
            )
            _require(response, {200})
            self._token = self.client.parse(response, AuthToken).token
        return self._token

    def authenticate_response(self, username: str, password: str) -> httpx.Response:
        """Raw auth call, used by negative tests that must inspect the body."""

        return self.client.post("/auth", json={"username": username, "password": password})

    def parse_auth_failure(self, response: httpx.Response) -> AuthFailure:
        return self.client.parse(response, AuthFailure)

    def auth_headers(self) -> dict[str, str]:
        return {"Cookie": f"token={self.authenticate()}"}

    # --- Booking CRUD ---------------------------------------------------

    def create(self, payload: Booking) -> CreatedBooking:
        response = self.client.post("/booking", json=payload.model_dump())
        _require(response, {200})
        return self.client.parse(response, CreatedBooking)

    def get_response(self, booking_id: int) -> httpx.Response:
        """Raw GET, so negative tests can assert 404 without an exception."""

        return self.client.get(f"/booking/{booking_id}")

    def get(self, booking_id: int) -> Booking:
        response = self.get_response(booking_id)
        _require(response, {200})
        return self.client.parse(response, Booking)

    def list_ids(self, **params: str) -> list[int]:
        response = self.client.get("/booking", params=params)
        _require(response, {200})
        return [entry.bookingid for entry in self.client.parse_list(response, BookingId)]

    def replace(self, booking_id: int, payload: Booking) -> httpx.Response:
        return self.client.put(
            f"/booking/{booking_id}",
            json=payload.model_dump(),
            headers=self.auth_headers(),
        )

    def partial_update(self, booking_id: int, changes: dict[str, object]) -> httpx.Response:
        return self.client.patch(
            f"/booking/{booking_id}",
            json=changes,
            headers=self.auth_headers(),
        )

    def delete(self, booking_id: int) -> httpx.Response:
        return self.client.delete(f"/booking/{booking_id}", headers=self.auth_headers())


def _require(response: httpx.Response, expected: set[int]) -> None:
    if response.status_code not in expected:
        raise ApiRequestError(response, expected)
