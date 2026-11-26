"""Shared fixtures and reporting hooks.

Scope strategy:

* `settings` and the API client are session-scoped: configuration is read once,
  and one connection pool serves the whole run.
* `booking_factory` is function-scoped so every test owns the records it creates
  and deletes them in teardown, even when it fails midway.
"""

from __future__ import annotations

import platform
from collections.abc import Callable, Generator, Iterator
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pytest

from qa_portfolio.api import ApiClient, BookingApi, Credentials
from qa_portfolio.config import Settings, get_settings
from qa_portfolio.data.factories import BookingOverrides, build_booking
from qa_portfolio.models.booking import CreatedBooking
from qa_portfolio.utils.logging import configure_logging, get_logger
from qa_portfolio.utils.paths import RESULTS_DIR

_log = get_logger("qa.fixtures")


#: `booking_factory` creates a booking and registers it for teardown deletion.
BookingFactory = Callable[..., CreatedBooking]


def pytest_configure(config: pytest.Config) -> None:
    """Create report folders and configure logging before collection."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    configure_logging(get_settings().log_level)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Expose each phase report on the item so fixtures can react to failures."""

    report = yield
    setattr(item, f"rep_{report.when}", report)
    return report


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write Allure environment details so the report explains where it ran."""

    alluredir = session.config.getoption("--alluredir", default=None)
    if not alluredir:
        return

    settings = get_settings()
    target = Path(alluredir) / "environment.properties"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            [
                f"Target.UI={settings.base_url}",
                f"Target.API={settings.api_base_url}",
                f"Python={platform.python_version()}",
                f"Platform={platform.platform()}",
                f"Pytest={_package_version('pytest')}",
                f"Playwright={_package_version('playwright')}",
                f"ExitStatus={exitstatus}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:  # pragma: no cover - packaging edge case
        return "unknown"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def api_client(settings: Settings) -> Iterator[ApiClient]:
    with ApiClient(base_url=settings.api_base_url, timeout=settings.request_timeout) as client:
        yield client


@pytest.fixture(scope="session")
def booking_api(api_client: ApiClient, settings: Settings) -> BookingApi:
    return BookingApi(
        api_client,
        Credentials(username=settings.booker_username, password=settings.booker_password),
    )


@pytest.fixture
def booking_factory(booking_api: BookingApi) -> Iterator[BookingFactory]:
    """Provide a create helper that deletes everything it created."""

    created_ids: list[int] = []

    def create(overrides: BookingOverrides | None = None) -> CreatedBooking:
        booking = booking_api.create(build_booking(overrides))
        created_ids.append(booking.bookingid)
        return booking

    yield create

    for booking_id in created_ids:
        response = booking_api.delete(booking_id)
        # 404/405 mean the test (or another cleanup) already removed the record;
        # that is a pass, not a cleanup failure.
        if response.status_code not in {200, 201, 404, 405}:
            _log.warning(
                "Cleanup failed for booking %s (status %s)", booking_id, response.status_code
            )
