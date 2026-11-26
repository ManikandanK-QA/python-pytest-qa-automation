"""Authenticated header: cart entry point and item-count badge.

Extracted so every page object shares one definition instead of repeating the
same selectors.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page


class Header:
    """Header rendered on every signed-in SauceDemo page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def cart_link(self) -> Locator:
        return self.page.locator(".shopping_cart_link")

    @property
    def cart_badge(self) -> Locator:
        return self.page.locator(".shopping_cart_badge")

    def open_cart(self) -> None:
        self.cart_link.click()
