"""
Amazon.in connector using the official Selling Partner API (SP-API).

IMPORTANT (honesty): this implements the REAL SP-API call flow, but it needs
YOUR credentials (see secrets.yaml) and an approved Professional seller +
SP-API app. It has NOT been tested against a live account from here - you must
plug in your keys and verify. If credentials are missing, it safely reports
"not configured" instead of erroring.

Docs: https://developer-docs.amazon.com/sp-api/
"""

from __future__ import annotations

import json
import time

try:
    import requests
except ImportError:
    requests = None

from channels.base import ChannelConnector
from channels.credentials import creds_for

LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"


class AmazonConnector(ChannelConnector):
    name = "Amazon"

    def __init__(self):
        self.c = creds_for("Amazon")
        self._token = None
        self._token_exp = 0

    # -- is this connector ready to go live? ---------------------------
    def configured(self) -> bool:
        needed = ("refresh_token", "client_id", "client_secret", "seller_id")
        return requests is not None and all(self.c.get(k) for k in needed)

    def _not_configured(self, action: str) -> dict:
        return {"channel": self.name, "status": "dry-run",
                "message": f"[Amazon] {action} prepared. Add SP-API keys in "
                           f"secrets.yaml to publish live."}

    # -- auth: exchange refresh token for a short-lived access token ----
    def _access_token(self) -> str | None:
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        try:
            resp = requests.post(LWA_TOKEN_URL, data={
                "grant_type": "refresh_token",
                "refresh_token": self.c["refresh_token"],
                "client_id": self.c["client_id"],
                "client_secret": self.c["client_secret"],
            }, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            self._token = j["access_token"]
            self._token_exp = time.time() + int(j.get("expires_in", 3600))
            return self._token
        except Exception as e:
            return None

    def _headers(self) -> dict:
        return {"x-amz-access-token": self._access_token() or "",
                "content-type": "application/json"}

    def _host(self) -> str:
        return self.c.get("region_host", "https://sellingpartnerapi-eu.amazon.com")

    # -- operations -----------------------------------------------------
    def publish_listing(self, product: dict, listing_text: str) -> dict:
        if not self.configured():
            return self._not_configured(f"Listing for '{product.get('name')}'")
        token = self._access_token()
        if not token:
            return {"channel": self.name, "status": "error",
                    "message": "[Amazon] Could not authenticate. Check your keys."}
        sku = product.get("sku") or f"SKU-{product.get('id','')}"
        url = (f"{self._host()}/listings/2021-08-01/items/"
               f"{self.c['seller_id']}/{sku}"
               f"?marketplaceIds={self.c.get('marketplace_id','A21TJRUUN4KGV')}")
        # Minimal listing payload - real attributes depend on your product type.
        body = {
            "productType": product.get("amazon_product_type", "PRODUCT"),
            "requirements": "LISTING",
            "attributes": {
                "item_name": [{"value": product.get("name", "")}],
                "list_price": [{"value": _f(product.get("price"))}],
            },
        }
        try:
            r = requests.put(url, headers=self._headers(),
                             data=json.dumps(body), timeout=45)
            ok = r.status_code in (200, 202)
            return {"channel": self.name,
                    "status": "published" if ok else "error",
                    "message": f"[Amazon] SP-API responded {r.status_code}: "
                               f"{r.text[:180]}"}
        except Exception as e:
            return {"channel": self.name, "status": "error",
                    "message": f"[Amazon] Request failed: {e}"}

    def update_price(self, product: dict, price: float) -> dict:
        if not self.configured():
            return self._not_configured(f"Price {price} for '{product.get('name')}'")
        # Price updates use the same Listings Items PATCH endpoint.
        return self._patch(product, [{"op": "replace",
                                      "path": "/attributes/list_price",
                                      "value": [{"value": price}]}],
                           f"price -> {price}")

    def sync_stock(self, product: dict, quantity: int) -> dict:
        if not self.configured():
            return self._not_configured(f"Stock {quantity} for '{product.get('name')}'")
        return self._patch(product, [{"op": "replace",
                                      "path": "/attributes/fulfillment_availability",
                                      "value": [{"quantity": quantity}]}],
                           f"stock -> {quantity}")

    def _patch(self, product: dict, patches: list, what: str) -> dict:
        sku = product.get("sku") or f"SKU-{product.get('id','')}"
        url = (f"{self._host()}/listings/2021-08-01/items/"
               f"{self.c['seller_id']}/{sku}"
               f"?marketplaceIds={self.c.get('marketplace_id','A21TJRUUN4KGV')}")
        try:
            r = requests.patch(url, headers=self._headers(),
                               data=json.dumps({"productType": "PRODUCT",
                                                "patches": patches}), timeout=45)
            ok = r.status_code in (200, 202)
            return {"channel": self.name,
                    "status": "updated" if ok else "error",
                    "message": f"[Amazon] {what}: HTTP {r.status_code}"}
        except Exception as e:
            return {"channel": self.name, "status": "error",
                    "message": f"[Amazon] {what} failed: {e}"}

    def fetch_orders(self) -> list[dict]:
        if not self.configured():
            return []
        url = (f"{self._host()}/orders/v0/orders"
               f"?MarketplaceIds={self.c.get('marketplace_id','A21TJRUUN4KGV')}"
               f"&CreatedAfter=2024-01-01T00:00:00Z")
        try:
            r = requests.get(url, headers=self._headers(), timeout=45)
            if r.status_code == 200:
                return r.json().get("payload", {}).get("Orders", [])
        except Exception:
            pass
        return []


def _f(v) -> float:
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0
