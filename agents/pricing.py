"""Pricing Agent - competitive prices, category-accurate fees, and GST (India)."""

from __future__ import annotations

from core.agent import Agent

# Category-accurate commission estimates (%) per Indian marketplace.
# These are approximate/illustrative - tune for your exact sub-category.
# Structure: MARKETPLACE -> { category: fee_fraction }, plus a "_default".
CATEGORY_FEES = {
    "Flipkart": {
        "apparel": 0.20, "electronics": 0.10, "home_kitchen": 0.15,
        "beauty": 0.18, "books": 0.12, "toys": 0.18, "footwear": 0.22,
        "jewellery": 0.20, "mobile_accessories": 0.15, "_default": 0.18,
    },
    "Amazon": {
        "apparel": 0.18, "electronics": 0.08, "home_kitchen": 0.14,
        "beauty": 0.16, "books": 0.12, "toys": 0.15, "footwear": 0.18,
        "jewellery": 0.20, "mobile_accessories": 0.14, "_default": 0.16,
    },
    "Myntra": {
        "apparel": 0.32, "footwear": 0.30, "beauty": 0.25, "jewellery": 0.28,
        "_default": 0.30,
    },
    "Ajio": {
        "apparel": 0.30, "footwear": 0.28, "beauty": 0.24, "jewellery": 0.26,
        "_default": 0.29,
    },
    "Meesho": {
        "apparel": 0.03, "electronics": 0.02, "home_kitchen": 0.03,
        "beauty": 0.03, "_default": 0.03,
    },
    # legacy/global fallbacks if you re-add these channels
    "eBay": {"_default": 0.13}, "Etsy": {"_default": 0.10},
    "Shopify": {"_default": 0.03}, "Facebook Marketplace": {"_default": 0.05},
}


class PricingAgent(Agent):
    name = "Piero"
    role = "Pricing & Margins Analyst"
    emoji = "[PRICE]"
    keywords = ["price", "pricing", "margin", "profit", "discount", "markdown",
                "fee", "cost", "cheap", "expensive", "gst", "tax"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role} for an Indian e-commerce "
            f"seller. You recommend competitive prices per marketplace, "
            f"accounting for category commission, GST and target margin. Show "
            f"the math briefly. Currency: INR (Rs)."
        )

    def _fee_for(self, channel: str, category: str) -> float:
        table = CATEGORY_FEES.get(channel, {"_default": 0.10})
        cat = (category or "").lower().replace(" ", "_").replace("&", "")
        # normalise a few common spellings
        alias = {"home": "home_kitchen", "kitchen": "home_kitchen",
                 "clothes": "apparel", "clothing": "apparel",
                 "shoes": "footwear", "mobile": "mobile_accessories",
                 "jewelry": "jewellery"}
        cat = alias.get(cat, cat)
        return table.get(cat, table.get("_default", 0.10))

    def _fallback(self, task: str, product: dict | None) -> str:
        p = product or {}
        cost = _to_float(p.get("cost"))
        base = _to_float(p.get("price")) or (cost * 1.6 if cost else 0)
        if not base:
            return ("[Piero] I need a 'price' or 'cost' on the product to run "
                    "pricing math. Add one and ask again.")

        gst = float(self.business.get("gst_percent", 18))
        gst_mode = str(self.business.get("gst_mode", "inclusive")).lower()
        category = p.get("category") or self.business.get("category", "general")

        out = [f"=== PRICING (INR) for {p.get('name','product')} ==="]
        out.append(f"Category: {category}  |  GST: {int(gst)}% ({gst_mode})")
        if cost:
            out.append(f"Unit cost: Rs {cost:.2f}")
        out.append("")

        best_net, best_ch = -1e9, None
        for ch in self.channels:
            fee = self._fee_for(ch, category)
            # base already targets covering the marketplace fee
            pre_gst = base * (1 + fee)
            if gst_mode == "extra":
                # GST added on top -> buyer pays more, GST is separate
                gst_component = round(pre_gst * gst / 100, 2)
                list_price = round(pre_gst + gst_component, 2)
            else:  # inclusive
                list_price = round(pre_gst, 2)
                gst_component = round(list_price - list_price / (1 + gst / 100), 2)
            fee_amount = round(list_price * fee, 2) if gst_mode == "extra" \
                else round(list_price * fee, 2)
            net = round(list_price - fee_amount - gst_component, 2)
            margin = net - cost if cost else None
            if net > best_net:
                best_net, best_ch = net, ch
            margin_str = f", margin Rs {margin:.2f}" if margin is not None else ""
            out.append(
                f"- {ch}: list Rs {list_price:.2f}  "
                f"(fee {int(fee*100)}% = Rs {fee_amount:.2f}, "
                f"GST = Rs {gst_component:.2f}, you net Rs {net:.2f}{margin_str})"
            )
        if best_ch:
            out.append(f"\nBest take-home: {best_ch} (Rs {best_net:.2f} net).")
        note = ("GST is added on top of your price." if gst_mode == "extra"
                else "List price is GST-inclusive (as buyers see it).")
        out.append(f"Note: {note} Input tax credit not included.")
        return "\n".join(out)


def _to_float(v) -> float:
    try:
        return float(str(v).replace("Rs", "").replace("INR", "")
                     .replace("\u20b9", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0
