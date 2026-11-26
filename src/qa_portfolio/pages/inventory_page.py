"""SauceDemo product catalogue."""

from __future__ import annotations

from typing import Literal

from playwright.sync_api import Locator, Page

from qa_portfolio.pages.base_page import BasePage
from qa_portfolio.pages.components.header import Header

SortOption = Literal["az", "za", "lohi", "hilo"]


class InventoryPage(BasePage):
    """Product list with sorting and add/remove actions."""

    path = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.title: Locator = page.locator(".title")
        self.items: Locator = page.locator(".inventory_item")
        self._sort_dropdown: Locator = page.get_by_test_id("product-sort-container")
        self._product_names: Locator = page.locator(".inventory_item_name")
        self._product_prices: Locator = page.locator(".inventory_item_price")

    def item_by_name(self, name: str) -> Locator:
        return self.items.filter(has_text=name)

    def sort_by(self, option: SortOption) -> None:
        self._sort_dropdown.select_option(option)

    def add_to_cart(self, product_name: str) -> None:
        self.item_by_name(product_name).get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, product_name: str) -> None:
        self.item_by_name(product_name).get_by_role("button", name="Remove").click()

    def open_cart(self) -> None:
        self.header.open_cart()

    def product_names(self) -> list[str]:
        return self._product_names.all_text_contents()

    def product_prices(self) -> list[float]:
        return [float(price.replace("$", "")) for price in self._product_prices.all_text_contents()]
