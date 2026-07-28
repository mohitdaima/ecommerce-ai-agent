"""Pricing Agent - suggests competitive prices and margins per marketplace."""

from __future__ import annotations

from core.agent import Agent

# Rough per-marketplace commission estimates (%) so suggestions account for
# fees. Indian marketplaces. These are approximate and CATEGORY-DEPENDENT -
# tweak them for your real category. Free, built-in heuristics.
MARKETPLACE_FEES = {
    "Flipkart": 0.18,   # ~5-25% commission by category (+ shipping/collection)
    "Amazon": 0.16,     # Amazon.in referral fee ~5-20% by category
    "Myntra": 0.30,     # apparel commissions are high, often ~25-45%
    "Meesho": 0.03,     # famously low / 0% commission on many categories
    # legacy examples still supported if you re-add them:
    "eBay": 0.13, "Etsy": 0.10, "Shopify": 0.03,
    "Facebook Marketplace": 0.05,
}


class PricingAgent(Agent):
    name = "Piero"
    role = "Pricing & Margins Analyst"
    emoji = "[PRICE]"
    keywords = ["price", "pricing", "margin", "profit", "discount", "markdown",
                "fee", "cost", "cheap", "expensive"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You recommend competitive "
            f"prices per marketplace, accounting for marketplace fees and target "
            f"margin. Always show the math briefly. Currency: "
            f"{self.business.get('currency', 'USD')}."
        )

    def _fallback(self, task: str, product: dict | None) -> str:
        p = product or {}
        cur = self.business.get("currency", "USD")
        cost = _to_float(p.get("cost"))
        base = _to_float(p.get("price")) or (cost * 1.6 if cost else 0)
        if not base:
            return ("[Piero] I need a 'price' or 'cost' on the product to run "
                    "pricing math. Add one and ask again.")
        out = [f"=== PRICING SUGGESTIONS ({cur}) for {p.get('name','product')} ==="]
        if cost:
            out.append(f"Unit cost: {cost:.2f}")
        for ch in self.channels:
            fee = MARKETPLACE_FEES.get(ch, 0.10)
            # price so that after fee we keep a healthy margin over cost
            suggested = round(base * (1 + fee), 2)
            net = round(suggested * (1 - fee), 2)
            margin = f"{net - cost:.2f}" if cost else "n/a"
            out.append(
                f"- {ch}: list at {suggested:.2f} "
                f"(fee ~{int(fee*100)}%, you net ~{net:.2f}, margin ~{margin})"
            )
        # dynamically name the lowest-fee channel you actually sell on
        best = min(self.channels,
                   key=lambda c: MARKETPLACE_FEES.get(c, 0.10)) \
            if self.channels else None
        if best:
            out.append(f"\nTip: {best} has the lowest fees - it's usually your "
                       f"best-margin channel.")
        return "\n".join(out)


def _to_float(v) -> float:
    try:
        return float(str(v).replace("$", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0
