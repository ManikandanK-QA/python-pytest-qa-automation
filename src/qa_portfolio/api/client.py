"""Thin typed wrapper around httpx.

Owns transport concerns only: base URL, JSON handling, timeouts and request
logging. Endpoint objects own paths and payload shapes; specs own assertions.
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from qa_portfolio.api.errors import ApiContractError, ApiShapeError
from qa_portfolio.utils.logging import get_logger

ModelT = TypeVar("ModelT", bound=BaseModel)

_log = get_logger("qa.api")


class ApiClient:
    """Reusable HTTP client with contract parsing."""

    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"Accept": "application/json"},
            follow_redirects=True,
        )

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._send("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._send("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._send("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._send("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._send("DELETE", path, **kwargs)

    def parse(self, response: httpx.Response, model: type[ModelT]) -> ModelT:
        """Validate a response body against `model` or raise `ApiContractError`."""

        payload = self._json(response)
        try:
            return model.model_validate(payload)
        except ValidationError as error:
            raise ApiContractError(response, error) from error

    def parse_list(self, response: httpx.Response, model: type[ModelT]) -> list[ModelT]:
        """Validate a JSON array of `model` documents."""

        payload = self._json(response)
        if not isinstance(payload, list):
            raise ApiShapeError(response, f"expected a JSON array, got {type(payload).__name__}")

        parsed: list[ModelT] = []
        for index, item in enumerate(payload):
            try:
                parsed.append(model.model_validate(item))
            except ValidationError as error:
                raise ApiContractError(response, error) from error
            except TypeError as error:  # pragma: no cover - defensive
                raise ApiShapeError(response, f"item {index} is not an object") from error
        return parsed

    def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        started = perf_counter()
        response = self._client.request(method, path, **kwargs)
        duration_ms = round((perf_counter() - started) * 1000, 1)

        # Expected negative responses (404/403) are part of the suite; only
        # server errors are worth a warning in the CI log.
        level = _log.warning if response.status_code >= 500 else _log.debug
        level(
            "%s %s -> %s (%sms)",
            method,
            path,
            response.status_code,
            duration_ms,
        )
        return response

    @staticmethod
    def _json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as error:
            raise ApiShapeError(
                response,
                f"body is not valid JSON ({error}): {response.text[:200]}",
            ) from error
