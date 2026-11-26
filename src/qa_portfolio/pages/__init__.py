"""Page objects: intent and locators only, no assertions."""

from qa_portfolio.pages.base_page import BasePage
from qa_portfolio.pages.cart_page import CartPage
from qa_portfolio.pages.checkout_information_page import CheckoutInformationPage
from qa_portfolio.pages.checkout_overview_page import CheckoutOverviewPage
from qa_portfolio.pages.inventory_page import InventoryPage
from qa_portfolio.pages.login_page import LoginPage

__all__ = [
    "BasePage",
    "CartPage",
    "CheckoutInformationPage",
    "CheckoutOverviewPage",
    "InventoryPage",
    "LoginPage",
]
