"""Listing Agent - writes optimized product listings for each marketplace."""

from __future__ import annotations

from core.agent import Agent


class ListingAgent(Agent):
    name = "Livia"
    role = "Product Listing Specialist"
    emoji = "[LIST]"
    # keywords the Manager uses to route tasks to this agent
    keywords = ["listing", "list", "title", "description", "publish", "post product",
                "write", "copy", "product page", "bullet"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You write high-converting "
            f"e-commerce listings. For each requested marketplace produce: a "
            f"punchy SEO title (<=200 chars), 5 benefit-driven bullet points, and "
            f"a persuasive description. Tone: {self.business.get('tone')}. "
            f"Marketplaces: {', '.join(self.channels)}."
        )

    def _build_prompt(self, task: str, product: dict | None) -> str:
        p = self._format_product(product) if product else "(no product selected)"
        return (
            f"Owner request: {task}\n\nProduct:\n{p}\n\n"
            f"Create ready-to-paste listings for these marketplaces: "
            f"{', '.join(self.channels)}. Label each section clearly."
        )

    def _fallback(self, task: str, product: dict | None) -> str:
        p = product or {}
        name = p.get("name", "Your Product")
        feats = p.get("features", []) or ["High quality", "Great value",
                                          "Fast shipping", "Trusted seller",
                                          "Satisfaction guaranteed"]
        out = [f"=== LISTING DRAFTS for {name} ==="]
        for ch in self.channels:
            out.append(f"\n--- {ch} ---")
            out.append(f"Title: {name} - {', '.join(str(f) for f in feats[:2])}")
            out.append("Bullets:")
            for f in feats[:5]:
                out.append(f"  - {f}")
            desc = p.get("description") or f"Discover the {name}. " \
                "Designed to deliver quality and value you can trust."
            out.append(f"Description: {desc}")
        return "\n".join(out)
