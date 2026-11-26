"""Negative sign-in cases.

One array instead of five near-identical test bodies: a new case is a data
change, and the parametrised test id names the scenario in reports.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InvalidLoginScenario:
    """Credentials that must be rejected, plus the expected message."""

    name: str
    username: str
    password: str
    expected_error: str


INVALID_LOGIN_SCENARIOS: tuple[InvalidLoginScenario, ...] = (
    InvalidLoginScenario(
        name="locked_out_user",
        username="locked_out_user",
        password="secret_sauce",
        expected_error="Sorry, this user has been locked out",
    ),
    InvalidLoginScenario(
        name="wrong_password",
        username="standard_user",
        password="wrong_password",
        expected_error="Username and password do not match",
    ),
    InvalidLoginScenario(
        name="missing_username",
        username="",
        password="secret_sauce",
        expected_error="Username is required",
    ),
    InvalidLoginScenario(
        name="missing_password",
        username="standard_user",
        password="",
        expected_error="Password is required",
    ),
)
