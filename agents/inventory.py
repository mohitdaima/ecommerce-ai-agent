"""Inventory Agent - tracks stock and flags low/out-of-stock items."""

from __future__ import annotations

from core.agent import Agent

LOW_STOCK_THRESHOLD = 5


class InventoryAgent(Agent):
    name = "Ivan"
    role = "Inventory Manager"
    emoji = "[STOCK]"
    keywords = ["inventory", "stock", "restock", "quantity", "sold out",
                "out of stock", "low stock", "count"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You monitor stock levels "
            f"across marketplaces and recommend restocking actions clearly."
        )

    def handle(self, task: str, product: dict | None = None) -> str:
        # Inventory is data-driven, so we compute directly (works offline too),
        # then optionally let the LLM add commentary.
        report = self._stock_report()
        commentary = self.llm.generate(
            self._system_prompt(),
            f"Owner request: {task}\n\nCurrent stock report:\n{report}\n\n"
            "Give a short action recommendation.",
        )
        text = report + ("\n\nRecommendation:\n" + commentary if commentary else "")
        self.store.add_output(self.name, task[:80], text,
                              product["id"] if product else None)
        return text

    def _stock_report(self) -> str:
        products = self.store.list_products()
        if not products:
            return "[Inventory] No products yet. Add some first."
        lines = ["=== INVENTORY REPORT ==="]
        low = []
        for p in products:
            stock = p.get("stock", "?")
            flag = ""
            if isinstance(stock, (int, float)):
                if stock <= 0:
                    flag = "  <-- OUT OF STOCK"
                    low.append(p["name"])
                elif stock <= LOW_STOCK_THRESHOLD:
                    flag = "  <-- LOW, restock soon"
                    low.append(p["name"])
            lines.append(f"- {p['name']} (id {p['id']}): {stock} units{flag}")
        if low:
            lines.append("\nNeeds attention: " + ", ".join(low))
        else:
            lines.append("\nAll products healthy on stock.")
        return "\n".join(lines)
