"""Shared page behaviour: navigation only.

Page objects model *intent* (sign in, add to cart) and expose locators for the
specs to assert on. They deliberately contain no `expect` calls, so a failure
always points at the test line rather than at a framework helper.
"""

from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    """Base for every page object."""

    #: Path relative to the context's `base_url`.
    path: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self) -> None:
        """Navigate to this page using the context base URL."""

        self.page.goto(self.path, wait_until="domcontentloaded")
