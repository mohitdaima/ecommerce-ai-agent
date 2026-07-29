"""
Catalog-export connector for marketplaces WITHOUT a public developer API
(Myntra, Meesho, Ajio).

Since these platforms don't let outside apps post directly, the honest and
genuinely useful approach is to generate a clean bulk-upload catalog file
(CSV) that you upload in their seller panel. This connector really works - it
writes/updates a per-marketplace CSV in data/exports/.
"""

from __future__ import annotations

import csv
import os

from channels.base import ChannelConnector

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(HERE, "data", "exports")

FIELDS = ["sku", "name", "category", "mrp", "selling_price", "stock",
          "description", "keywords", "images"]


class CatalogExportConnector(ChannelConnector):
    """Writes each product as a row into <channel>_catalog.csv."""

    def __init__(self, name: str):
        self.name = name
        os.makedirs(EXPORT_DIR, exist_ok=True)
        self.path = os.path.join(EXPORT_DIR, f"{name.lower()}_catalog.csv")

    def _row(self, product: dict) -> dict:
        return {
            "sku": product.get("sku") or f"SKU-{product.get('id','')}",
            "name": product.get("name", ""),
            "category": product.get("category", ""),
            "mrp": product.get("price", ""),
            "selling_price": product.get("price", ""),
            "stock": product.get("stock", 0),
            "description": product.get("description", ""),
            "keywords": ", ".join(product.get("keywords", []) or []),
            "images": ", ".join(product.get("images", []) or []),
        }

    def _upsert(self, product: dict) -> None:
        rows = []
        sku = self._row(product)["sku"]
        if os.path.exists(self.path):
            with open(self.path, newline="", encoding="utf-8") as f:
                rows = [r for r in csv.DictReader(f) if r.get("sku") != sku]
        rows.append(self._row(product))
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)

    def publish_listing(self, product: dict, listing_text: str) -> dict:
        self._upsert(product)
        rel = os.path.relpath(self.path, HERE)
        return {"channel": self.name, "status": "exported",
                "message": f"[{self.name}] Added to bulk-upload file: {rel} "
                           f"- upload it in your {self.name} seller panel."}

    def update_price(self, product: dict, price: float) -> dict:
        product = dict(product, price=price)
        self._upsert(product)
        return {"channel": self.name, "status": "exported",
                "message": f"[{self.name}] Price {price} saved to catalog file."}

    def sync_stock(self, product: dict, quantity: int) -> dict:
        product = dict(product, stock=quantity)
        self._upsert(product)
        return {"channel": self.name, "status": "exported",
                "message": f"[{self.name}] Stock {quantity} saved to catalog file."}

    def fetch_orders(self) -> list[dict]:
        # No API - orders are managed in the seller panel.
        return []
