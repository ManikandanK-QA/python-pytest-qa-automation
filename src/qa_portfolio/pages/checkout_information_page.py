"""Checkout step one: customer information."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from qa_portfolio.pages.base_page import BasePage


class CheckoutInformationPage(BasePage):
    """Customer details form with validation."""

    path = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._first_name: Locator = page.get_by_test_id("firstName")
        self._last_name: Locator = page.get_by_test_id("lastName")
        self._postal_code: Locator = page.get_by_test_id("postalCode")
        self._continue_button: Locator = page.get_by_test_id("continue")
        self._cancel_button: Locator = page.get_by_test_id("cancel")
        self.error_banner: Locator = page.get_by_test_id("error")

    def fill_customer_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        self._first_name.fill(first_name)
        self._last_name.fill(last_name)
        self._postal_code.fill(postal_code)

    def continue_to_overview(self) -> None:
        self._continue_button.click()

    def cancel(self) -> None:
        self._cancel_button.click()
