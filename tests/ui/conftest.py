"""Browser fixtures and failure artefacts for UI tests.

Authentication is performed once per worker and reused through `storageState`,
so specs never pay for a UI login. Tests that exercise the sign-in form opt out
with the `browser_context_args(storage_state=None)` marker.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import allure
import pytest
from playwright.sync_api import Browser, Page, Playwright
from playwright.sync_api import Error as PlaywrightError

from qa_portfolio.config import Settings
from qa_portfolio.pages import LoginPage
from qa_portfolio.utils.logging import get_logger
from qa_portfolio.utils.paths import ARTIFACTS_DIR, AUTH_DIR

_log = get_logger("qa.ui")


@pytest.fixture(scope="session", autouse=True)
def _saucedemo_test_ids(playwright: Playwright) -> None:
    """SauceDemo marks elements with `data-test`, not the default `data-testid`."""

    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def auth_state(browser: Browser, settings: Settings) -> Path:
    """Sign in once and persist the session for the UI projects.

    The file is per xdist worker: two workers writing one path would race.
    """

    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    path = AUTH_DIR / f"standard-user-{worker}.json"
    path.unlink(missing_ok=True)

    context = browser.new_context(base_url=settings.base_url)
    page = context.new_page()
    try:
        login = LoginPage(page)
        login.goto()
        login.login(settings.sauce_username, settings.sauce_password)
        page.wait_for_url(re.compile(r"/inventory\.html$"), timeout=20_000)
        path.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(path))
    finally:
        context.close()

    return path


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], settings: Settings, auth_state: Path
) -> dict[str, Any]:
    """Add the demo base URL and the reused session to every context."""

    return {
        **browser_context_args,
        "base_url": settings.base_url,
        "storage_state": str(auth_state),
    }


@pytest.fixture(autouse=True)
def capture_failure_artifacts(page: Page, request: pytest.FixtureRequest) -> Iterator[None]:
    """Attach a screenshot and the page source to Allure when a UI test fails."""

    yield

    report = getattr(request.node, "rep_call", None)
    if report is None or not report.failed:
        return

    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    screenshot = ARTIFACTS_DIR / f"{slug}.png"

    try:
        page.screenshot(path=str(screenshot), full_page=True)
        # allure-python-commons ships without type hints.
        allure.attach.file(  # type: ignore[no-untyped-call]
            str(screenshot),
            name="failure screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    except PlaywrightError as error:
        _log.warning("Could not capture screenshot for %s: %s", request.node.nodeid, error)

    try:
        allure.attach(
            page.content(),
            name="page source",
            attachment_type=allure.attachment_type.HTML,
        )
    except PlaywrightError as error:
        _log.warning("Could not capture page source for %s: %s", request.node.nodeid, error)
