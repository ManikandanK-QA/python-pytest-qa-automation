"""Product catalogue: contents, sorting and cart badge synchronisation."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from qa_portfolio.data.products import PRODUCT_COUNT, PRODUCTS
from qa_portfolio.pages import InventoryPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.fixture(autouse=True)
def catalogue(page: Page) -> InventoryPage:
    """Open the catalogue and wait for the first product, without asserting."""

    inventory = InventoryPage(page)
    inventory.goto()
    inventory.items.first.wait_for(state="visible")
    return inventory


@pytest.mark.smoke
def test_lists_every_catalogue_product(catalogue: InventoryPage) -> None:
    expect(catalogue.items).to_have_count(PRODUCT_COUNT)

    names = catalogue.product_names()
    assert PRODUCTS["backpack"].name in names
    assert PRODUCTS["fleece_jacket"].name in names


def test_sorts_products_by_price_ascending(catalogue: InventoryPage) -> None:
    catalogue.sort_by("lohi")

    prices = catalogue.product_prices()
    assert len(prices) == PRODUCT_COUNT
    assert prices == sorted(prices)
    assert prices[0] == PRODUCTS["onesie"].price
    assert prices[-1] == PRODUCTS["fleece_jacket"].price


def test_adds_and_removes_products_keeping_the_badge_in_sync(
    catalogue: InventoryPage,
) -> None:
    catalogue.add_to_cart(PRODUCTS["backpack"].name)
    expect(catalogue.header.cart_badge).to_have_text("1")

    catalogue.add_to_cart(PRODUCTS["bike_light"].name)
    expect(catalogue.header.cart_badge).to_have_text("2")

    catalogue.remove_from_cart(PRODUCTS["bike_light"].name)
    expect(catalogue.header.cart_badge).to_have_text("1")
