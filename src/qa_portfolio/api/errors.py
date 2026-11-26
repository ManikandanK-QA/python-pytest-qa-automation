"""Typed failures raised by the API layer.

Every error carries the failing request and response, so a CI log is enough to
triage without re-running the test.
"""

from __future__ import annotations

import httpx
from pydantic import ValidationError

_BODY_PREVIEW = 800


class ApiError(RuntimeError):
    """Base class for API-layer failures."""


class ApiRequestError(ApiError):
    """The service answered with an unexpected status."""

    def __init__(self, response: httpx.Response, expected: set[int]) -> None:
        request = response.request
        body = response.text[:_BODY_PREVIEW]
        super().__init__(
            f"{request.method} {request.url} returned {response.status_code} "
            f"(expected {sorted(expected)}): {body}"
        )
        self.response = response


class ApiShapeError(ApiError):
    """The body is not the JSON shape the endpoint promises."""

    def __init__(self, response: httpx.Response, detail: str) -> None:
        request = response.request
        super().__init__(
            f"Unexpected response shape for {request.method} {request.url} "
            f"(status {response.status_code}): {detail}"
        )
        self.response = response


class ApiContractError(ApiError):
    """The payload does not match the documented contract."""

    def __init__(self, response: httpx.Response, error: ValidationError) -> None:
        request = response.request
        details = "\n".join(
            f"  - {'.'.join(str(part) for part in issue['loc']) or '(root)'}: {issue['msg']}"
            for issue in error.errors()
        )
        super().__init__(
            f"Contract violation for {request.method} {request.url} "
            f"(status {response.status_code}):\n{details}"
        )
        self.response = response
