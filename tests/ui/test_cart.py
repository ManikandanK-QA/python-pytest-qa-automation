"""Shopping cart: contents, removal and navigation."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from qa_portfolio.data.products import PRODUCTS
from qa_portfolio.pages import CartPage, InventoryPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.fixture(autouse=True)
def cart(page: Page) -> CartPage:
    """Add two products from the catalogue and open the cart."""

    inventory = InventoryPage(page)
    inventory.goto()
    inventory.items.first.wait_for(state="visible")
    inventory.add_to_cart(PRODUCTS["backpack"].name)
    inventory.add_to_cart(PRODUCTS["onesie"].name)
    inventory.open_cart()
    page.wait_for_url(re.compile(r"/cart\.html$"))

    return CartPage(page)


def test_shows_every_product_added_from_the_catalogue(cart: CartPage) -> None:
    expect(cart.items).to_have_count(2)
    expect(cart.item_by_name(PRODUCTS["backpack"].name)).to_be_visible()
    expect(cart.item_by_name(PRODUCTS["onesie"].name)).to_be_visible()


def test_removes_a_product_and_updates_the_badge(cart: CartPage) -> None:
    cart.remove(PRODUCTS["backpack"].name)

    expect(cart.items).to_have_count(1)
    expect(cart.header.cart_badge).to_have_text("1")


def test_continues_shopping_back_to_the_catalogue(cart: CartPage, page: Page) -> None:
    cart.continue_shopping()

    expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(InventoryPage(page).title).to_have_text("Products")
