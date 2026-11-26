"""SauceDemo sign-in page."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from qa_portfolio.pages.base_page import BasePage


class LoginPage(BasePage):
    """Sign-in form with inline validation errors."""

    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input: Locator = page.get_by_test_id("username")
        self.password_input: Locator = page.get_by_test_id("password")
        self.login_button: Locator = page.get_by_test_id("login-button")
        self.error_banner: Locator = page.get_by_test_id("error")

    def login(self, username: str, password: str) -> None:
        """Fill the form and submit it, including empty credentials."""

        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
