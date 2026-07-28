"""
Base connector interface for marketplaces.

This is the SAFE, OPTIONAL bridge to the real world. By default the team just
generates content for you to paste. If/when you want automation, implement one
of these per marketplace using its official API (Amazon SP-API, eBay API, Etsy
API, Shopify Admin API, ...). Most are free to obtain with your own seller
account.

Keeping this as an interface means the free, local core never depends on any
paid service.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ChannelConnector(ABC):
    name: str = "channel"

    @abstractmethod
    def publish_listing(self, product: dict, listing_text: str) -> dict:
        """Publish/update a listing. Return a result dict with status + url."""
        raise NotImplementedError

    @abstractmethod
    def update_price(self, product: dict, price: float) -> dict:
        """Update the price of an existing listing."""
        raise NotImplementedError

    @abstractmethod
    def sync_stock(self, product: dict, quantity: int) -> dict:
        """Push a new stock quantity to the marketplace."""
        raise NotImplementedError

    @abstractmethod
    def fetch_orders(self) -> list[dict]:
        """Return new/open orders from the marketplace."""
        raise NotImplementedError


class DryRunConnector(ChannelConnector):
    """Default connector: doesn't touch any real marketplace.

    It just reports what *would* happen, so you can test the full flow for free
    and with zero risk. Swap in a real connector when ready.
    """

    def __init__(self, name: str):
        self.name = name

    def publish_listing(self, product: dict, listing_text: str) -> dict:
        return {"channel": self.name, "status": "dry-run",
                "message": f"Would publish '{product.get('name')}' to {self.name}."}

    def update_price(self, product: dict, price: float) -> dict:
        return {"channel": self.name, "status": "dry-run",
                "message": f"Would set {product.get('name')} price to {price} on {self.name}."}

    def sync_stock(self, product: dict, quantity: int) -> dict:
        return {"channel": self.name, "status": "dry-run",
                "message": f"Would set {product.get('name')} stock to {quantity} on {self.name}."}

    def fetch_orders(self) -> list[dict]:
        return []
