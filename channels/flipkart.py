"""
Flipkart connector using the official Flipkart Marketplace API.

Honesty note: real API flow, but needs YOUR Flipkart app credentials (see
secrets.yaml) and an approved seller account. Not tested against a live account
from here - plug in your keys and verify. Missing keys -> safe dry-run.

Docs: https://seller.flipkart.com/api-docs/FMSAPI.html
"""

from __future__ import annotations

import base64
import json
import time

try:
    import requests
except ImportError:
    requests = None

from channels.base import ChannelConnector
from channels.credentials import creds_for

TOKEN_URL = ("https://api.flipkart.net/oauth-service/oauth/token"
             "?grant_type=client_credentials&scope=Seller_Api")
API = "https://api.flipkart.net/sellers"


class FlipkartConnector(ChannelConnector):
    name = "Flipkart"

    def __init__(self):
        self.c = creds_for("Flipkart")
        self._token = None
        self._token_exp = 0

    def configured(self) -> bool:
        return requests is not None and bool(self.c.get("app_id")) \
            and bool(self.c.get("app_secret"))

    def _not_configured(self, action: str) -> dict:
        return {"channel": self.name, "status": "dry-run",
                "message": f"[Flipkart] {action} prepared. Add app_id/app_secret "
                           f"in secrets.yaml to publish live."}

    def _access_token(self) -> str | None:
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        basic = base64.b64encode(
            f"{self.c['app_id']}:{self.c['app_secret']}".encode()).decode()
        try:
            r = requests.get(TOKEN_URL,
                             headers={"Authorization": f"Basic {basic}"},
                             timeout=30)
            r.raise_for_status()
            j = r.json()
            self._token = j["access_token"]
            self._token_exp = time.time() + int(j.get("expires_in", 3600))
            return self._token
        except Exception:
            return None

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._access_token()}",
                "Content-Type": "application/json"}

    def publish_listing(self, product: dict, listing_text: str) -> dict:
        if not self.configured():
            return self._not_configured(f"Listing for '{product.get('name')}'")
        if not self._access_token():
            return {"channel": self.name, "status": "error",
                    "message": "[Flipkart] Could not authenticate. Check keys."}
        # Flipkart listings are created via the Listings API against an existing
        # catalog product (FSN). This posts the listing payload.
        sku = product.get("sku") or f"SKU-{product.get('id','')}"
        body = {"sku": sku, "listings": {
            "mrp": _f(product.get("price")),
            "selling_price": _f(product.get("price")),
            "listing_status": "ACTIVE",
            "stock_count": product.get("stock", 0),
        }}
        try:
            r = requests.post(f"{API}/listings/v3/create",
                              headers=self._headers(),
                              data=json.dumps(body), timeout=45)
            ok = r.status_code in (200, 201, 202)
            return {"channel": self.name,
                    "status": "published" if ok else "error",
                    "message": f"[Flipkart] HTTP {r.status_code}: {r.text[:180]}"}
        except Exception as e:
            return {"channel": self.name, "status": "error",
                    "message": f"[Flipkart] Request failed: {e}"}

    def update_price(self, product: dict, price: float) -> dict:
        if not self.configured():
            return self._not_configured(f"Price {price} for '{product.get('name')}'")
        sku = product.get("sku") or f"SKU-{product.get('id','')}"
        body = {"sku": sku, "selling_price": price}
        return self._post("/listings/v3/prices", body, f"price -> {price}")

    def sync_stock(self, product: dict, quantity: int) -> dict:
        if not self.configured():
            return self._not_configured(f"Stock {quantity} for '{product.get('name')}'")
        sku = product.get("sku") or f"SKU-{product.get('id','')}"
        body = {"sku": sku, "inventory": quantity}
        return self._post("/listings/v3/inventory", body, f"stock -> {quantity}")

    def _post(self, path: str, body: dict, what: str) -> dict:
        try:
            r = requests.post(f"{API}{path}", headers=self._headers(),
                              data=json.dumps(body), timeout=45)
            ok = r.status_code in (200, 201, 202)
            return {"channel": self.name,
                    "status": "updated" if ok else "error",
                    "message": f"[Flipkart] {what}: HTTP {r.status_code}"}
        except Exception as e:
            return {"channel": self.name, "status": "error",
                    "message": f"[Flipkart] {what} failed: {e}"}

    def fetch_orders(self) -> list[dict]:
        if not self.configured() or not self._access_token():
            return []
        try:
            r = requests.post(f"{API}/orders/search", headers=self._headers(),
                              data=json.dumps({"filter": {"states": ["APPROVED"]}}),
                              timeout=45)
            if r.status_code == 200:
                return r.json().get("orderItems", [])
        except Exception:
            pass
        return []


def _f(v) -> float:
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0
