"""Checkout step two: order overview and confirmation."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from qa_portfolio.pages.base_page import BasePage


class CheckoutOverviewPage(BasePage):
    """Order summary, total and the final confirmation message."""

    path = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items: Locator = page.locator(".cart_item")
        self.total: Locator = page.locator(".summary_total_label")
        self.order_confirmation: Locator = page.locator(".complete-header")
        self._finish_button: Locator = page.get_by_test_id("finish")

    def finish(self) -> None:
        self._finish_button.click()
