"""Analytics Agent - summarizes catalog/business health and gives insights."""

from __future__ import annotations

from core.agent import Agent


class AnalyticsAgent(Agent):
    name = "Ana"
    role = "Business Analytics Advisor"
    emoji = "[DATA]"
    keywords = ["analytics", "report", "insight", "summary", "overview",
                "performance", "sales", "dashboard", "stats", "how are we"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You turn catalog and store "
            f"data into clear insights and 3 concrete next actions."
        )

    def handle(self, task: str, product: dict | None = None) -> str:
        snapshot = self._snapshot()
        commentary = self.llm.generate(
            self._system_prompt(),
            f"Owner request: {task}\n\nData snapshot:\n{snapshot}\n\n"
            "Give 3 concrete, prioritized next actions.",
        )
        text = snapshot + ("\n\nInsights:\n" + commentary if commentary
                           else "\n\nInsights:\n" + self._fallback_insights())
        self.store.add_output(self.name, task[:80], text, None)
        return text

    def _snapshot(self) -> str:
        products = self.store.list_products()
        outputs = self.store.list_outputs()
        tasks = self.store.list_tasks()
        total_stock = sum(p.get("stock", 0) for p in products
                          if isinstance(p.get("stock"), (int, float)))
        cats = {}
        for p in products:
            cats[p.get("category", "uncategorized")] = \
                cats.get(p.get("category", "uncategorized"), 0) + 1
        lines = [
            "=== BUSINESS SNAPSHOT ===",
            f"Products in catalog: {len(products)}",
            f"Total units in stock: {total_stock}",
            f"Marketplaces: {', '.join(self.channels)}",
            f"Tasks completed by the team: {len(tasks)}",
            f"Content pieces generated: {len(outputs)}",
            "Categories: " + (", ".join(f"{k} ({v})" for k, v in cats.items())
                              or "none"),
        ]
        return "\n".join(lines)

    @staticmethod
    def _fallback_insights() -> str:
        return ("1. Ensure every product is listed on all marketplaces.\n"
                "2. Refresh low-stock items and pause ads for out-of-stock ones.\n"
                "3. Run a promo on your highest-margin channel (usually Shopify).")
