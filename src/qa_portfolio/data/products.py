"""SauceDemo catalogue, used by specs instead of repeating display names."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Product:
    """A catalogue entry."""

    name: str
    price: float


PRODUCTS: dict[str, Product] = {
    "backpack": Product("Sauce Labs Backpack", 29.99),
    "bike_light": Product("Sauce Labs Bike Light", 9.99),
    "bolt_tshirt": Product("Sauce Labs Bolt T-Shirt", 15.99),
    "fleece_jacket": Product("Sauce Labs Fleece Jacket", 49.99),
    "onesie": Product("Sauce Labs Onesie", 7.99),
    "red_tshirt": Product("Test.allTheThings() T-Shirt (Red)", 15.99),
}

PRODUCT_COUNT = len(PRODUCTS)
