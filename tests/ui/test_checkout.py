"""Checkout: end-to-end purchase and mandatory-field validation."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from qa_portfolio.data.products import PRODUCTS
from qa_portfolio.pages import (
    CartPage,
    CheckoutInformationPage,
    CheckoutOverviewPage,
    InventoryPage,
)

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.fixture(autouse=True)
def checkout_information(page: Page) -> CheckoutInformationPage:
    """Reach step one of checkout with a single product in the cart."""

    inventory = InventoryPage(page)
    inventory.goto()
    inventory.items.first.wait_for(state="visible")
    inventory.add_to_cart(PRODUCTS["backpack"].name)
    inventory.open_cart()
    page.wait_for_url(re.compile(r"/cart\.html$"))

    CartPage(page).checkout()
    page.wait_for_url(re.compile(r"/checkout-step-one\.html$"))

    return CheckoutInformationPage(page)


@pytest.mark.smoke
def test_completes_an_order_end_to_end(
    checkout_information: CheckoutInformationPage, page: Page
) -> None:
    checkout_information.fill_customer_information("Manikandan", "Kandasamy", "600001")
    checkout_information.continue_to_overview()
    expect(page).to_have_url(re.compile(r"/checkout-step-two\.html$"))

    overview = CheckoutOverviewPage(page)
    expect(overview.items).to_have_count(1)
    expect(overview.total).to_contain_text("Total: $")

    overview.finish()
    expect(page).to_have_url(re.compile(r"/checkout-complete\.html$"))
    expect(overview.order_confirmation).to_have_text("Thank you for your order!")


def test_blocks_checkout_when_the_postal_code_is_missing(
    checkout_information: CheckoutInformationPage,
) -> None:
    checkout_information.fill_customer_information("Manikandan", "Kandasamy", "")
    checkout_information.continue_to_overview()

    expect(checkout_information.error_banner).to_contain_text("Postal Code is required")
