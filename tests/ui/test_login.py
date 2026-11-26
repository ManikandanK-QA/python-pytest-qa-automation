"""Sign-in behaviour, including the negative matrix."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from qa_portfolio.config import Settings
from qa_portfolio.data.users import INVALID_LOGIN_SCENARIOS, InvalidLoginScenario
from qa_portfolio.pages import InventoryPage, LoginPage

# Authentication is the subject here, so every test starts signed out.
pytestmark = [
    pytest.mark.ui,
    pytest.mark.regression,
    pytest.mark.browser_context_args(storage_state=None),
]


@pytest.mark.smoke
def test_signs_in_with_valid_credentials(page: Page, settings: Settings) -> None:
    login = LoginPage(page)
    login.goto()
    login.login(settings.sauce_username, settings.sauce_password)

    expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(InventoryPage(page).title).to_have_text("Products")


@pytest.mark.parametrize(
    "scenario",
    INVALID_LOGIN_SCENARIOS,
    ids=[scenario.name for scenario in INVALID_LOGIN_SCENARIOS],
)
def test_rejects_invalid_credentials(page: Page, scenario: InvalidLoginScenario) -> None:
    login = LoginPage(page)
    login.goto()
    login.login(scenario.username, scenario.password)

    expect(login.error_banner).to_be_visible()
    expect(login.error_banner).to_contain_text(scenario.expected_error)
    expect(page).to_have_url(re.compile(r"^https://www\.saucedemo\.com/?$"))
