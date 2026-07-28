"""
Local data store - free, file-based (JSON). No database server, no cloud.

Keeps everything the team needs on your own disk:
  * products      - the product details YOU provide
  * tasks         - the task board (what you asked the agents to do)
  * outputs       - everything the agents generated (listings, posts, etc.)
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any


class Store:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.products_path = os.path.join(data_dir, "products.json")
        self.tasks_path = os.path.join(data_dir, "tasks.json")
        self.outputs_path = os.path.join(data_dir, "outputs.json")
        self.returns_path = os.path.join(data_dir, "returns.json")
        self._products = self._load(self.products_path, [])
        self._tasks = self._load(self.tasks_path, [])
        self._outputs = self._load(self.outputs_path, [])
        self._returns = self._load(self.returns_path, [])

    # -- low level ------------------------------------------------------
    @staticmethod
    def _load(path: str, default: Any) -> Any:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    @staticmethod
    def _save(path: str, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # -- products -------------------------------------------------------
    def add_product(self, product: dict) -> dict:
        product.setdefault("id", str(uuid.uuid4())[:8])
        product.setdefault("created_at", time.time())
        # replace if same id exists
        self._products = [p for p in self._products if p["id"] != product["id"]]
        self._products.append(product)
        self._save(self.products_path, self._products)
        return product

    def list_products(self) -> list[dict]:
        return list(self._products)

    def get_product(self, product_id: str) -> dict | None:
        for p in self._products:
            if p["id"] == product_id:
                return p
        return None

    def find_product(self, query: str) -> dict | None:
        """Fuzzy-ish lookup by id or name substring."""
        query_l = query.lower().strip()
        for p in self._products:
            if p["id"] == query_l:
                return p
        for p in self._products:
            if query_l in p.get("name", "").lower():
                return p
        return None

    def update_stock(self, product_id: str, qty: int) -> dict | None:
        p = self.get_product(product_id)
        if p:
            p["stock"] = qty
            self._save(self.products_path, self._products)
        return p

    # -- tasks ----------------------------------------------------------
    def add_task(self, description: str, assigned_to: str) -> dict:
        task = {
            "id": str(uuid.uuid4())[:8],
            "description": description,
            "assigned_to": assigned_to,
            "status": "done",  # agents complete synchronously in this build
            "created_at": time.time(),
        }
        self._tasks.append(task)
        self._save(self.tasks_path, self._tasks)
        return task

    def list_tasks(self) -> list[dict]:
        return list(self._tasks)

    # -- outputs --------------------------------------------------------
    def add_output(self, agent: str, title: str, content: str,
                   product_id: str | None = None) -> dict:
        out = {
            "id": str(uuid.uuid4())[:8],
            "agent": agent,
            "title": title,
            "content": content,
            "product_id": product_id,
            "created_at": time.time(),
        }
        self._outputs.append(out)
        self._save(self.outputs_path, self._outputs)
        return out

    def list_outputs(self) -> list[dict]:
        return list(self._outputs)

    # -- returns / RMAs -------------------------------------------------
    def add_return(self, product_id: str | None, product_name: str,
                   channel: str, reason: str, status: str = "requested",
                   restock: bool = False) -> dict:
        rma = {
            "rma": "RMA-" + str(uuid.uuid4())[:6].upper(),
            "product_id": product_id,
            "product_name": product_name,
            "channel": channel,
            "reason": reason,
            "status": status,          # requested | approved | received | refunded | closed
            "restock": restock,
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        self._returns.append(rma)
        self._save(self.returns_path, self._returns)
        return rma

    def update_return(self, rma_id: str, status: str) -> dict | None:
        for r in self._returns:
            if r["rma"].lower() == rma_id.lower():
                r["status"] = status
                r["updated_at"] = time.time()
                self._save(self.returns_path, self._returns)
                return r
        return None

    def list_returns(self) -> list[dict]:
        return list(self._returns)
