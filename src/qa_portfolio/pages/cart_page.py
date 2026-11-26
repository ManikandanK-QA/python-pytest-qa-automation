"""SauceDemo shopping cart."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from qa_portfolio.pages.base_page import BasePage
from qa_portfolio.pages.components.header import Header


class CartPage(BasePage):
    """Cart contents and checkout entry point."""

    path = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.items: Locator = page.locator(".cart_item")
        self._checkout_button: Locator = page.get_by_test_id("checkout")
        self._continue_shopping_button: Locator = page.get_by_test_id("continue-shopping")

    def item_by_name(self, name: str) -> Locator:
        return self.items.filter(has_text=name)

    def remove(self, product_name: str) -> None:
        self.item_by_name(product_name).get_by_role("button", name="Remove").click()

    def checkout(self) -> None:
        self._checkout_button.click()

    def continue_shopping(self) -> None:
        self._continue_shopping_button.click()
