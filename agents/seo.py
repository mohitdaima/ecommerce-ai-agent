"""SEO Agent - generates keywords, tags and search-optimized phrasing."""

from __future__ import annotations

from core.agent import Agent


class SEOAgent(Agent):
    name = "Seon"
    role = "SEO & Keyword Specialist"
    emoji = "[SEO]"
    keywords = ["seo", "keyword", "keywords", "tags", "search", "rank",
                "discoverability", "meta", "backlink"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You produce high-intent "
            f"keywords, long-tail phrases and marketplace tags that improve "
            f"discoverability. Group them by intent (broad, long-tail, tags)."
        )

    def _fallback(self, task: str, product: dict | None) -> str:
        p = product or {}
        name = p.get("name", "product").lower()
        cat = str(p.get("category", "")).lower()
        base = [w for w in (name.split() + cat.split()) if w]
        kws = set(p.get("keywords") or [])
        broad = list(kws) + base
        longtail = [f"best {name}", f"{name} for sale", f"buy {name} online",
                    f"affordable {name}", f"{name} {cat}".strip()]
        tags = [b.replace(" ", "") for b in broad][:13]
        return "\n".join([
            f"=== SEO KEYWORDS for {p.get('name','product')} ===",
            "Broad: " + ", ".join(dict.fromkeys(broad)) if broad else "Broad: -",
            "Long-tail: " + ", ".join(longtail),
            "Marketplace tags: " + ", ".join(dict.fromkeys(tags)),
        ])
