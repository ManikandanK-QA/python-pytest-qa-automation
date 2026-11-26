"""Pydantic contracts for the Restful Booker API.

Every response is validated against these models before an assertion runs, so
schema drift fails with the exact field path instead of a misleading assertion
message.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BookingDates(BaseModel):
    """Check-in and check-out dates in `YYYY-MM-DD` form."""

    model_config = ConfigDict(extra="ignore")

    checkin: str = Field(min_length=1)
    checkout: str = Field(min_length=1)


class Booking(BaseModel):
    """A booking as returned by Restful Booker."""

    model_config = ConfigDict(extra="ignore")

    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None


class BookingId(BaseModel):
    """One entry of the booking list endpoint."""

    model_config = ConfigDict(extra="ignore")

    bookingid: int = Field(gt=0)


class CreatedBooking(BaseModel):
    """Response of `POST /booking`."""

    model_config = ConfigDict(extra="ignore")

    bookingid: int = Field(gt=0)
    booking: Booking


class AuthToken(BaseModel):
    """Response of `POST /auth` with valid credentials."""

    model_config = ConfigDict(extra="ignore")

    token: str = Field(min_length=1)


class AuthFailure(BaseModel):
    """Restful Booker answers bad credentials with HTTP 200 and a reason."""

    model_config = ConfigDict(extra="ignore")

    reason: str
