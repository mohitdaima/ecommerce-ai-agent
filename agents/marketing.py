"""Marketing Agent - social posts, ad copy, email campaigns, promotions."""

from __future__ import annotations

from core.agent import Agent


class MarketingAgent(Agent):
    name = "Mara"
    role = "Marketing & Content Creator"
    emoji = "[MKTG]"
    keywords = ["marketing", "ad", "ads", "social", "instagram", "facebook",
                "tiktok", "email", "campaign", "promo", "promotion", "caption",
                "hashtag", "newsletter", "launch"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You create scroll-stopping "
            f"social captions (with hashtags), short ad copy, and email campaign "
            f"drafts. Tone: {self.business.get('tone')}. Keep it punchy and "
            f"platform-appropriate."
        )

    def _fallback(self, task: str, product: dict | None) -> str:
        p = product or {}
        name = p.get("name", "our product")
        feat = (p.get("features") or ["quality you can trust"])[0]
        tags = _hashtags(p)
        return "\n".join([
            f"=== MARKETING KIT for {name} ===",
            "\n[Instagram / Facebook caption]",
            f"Meet the {name} - {feat}. Tap to shop and see why customers love it! {tags}",
            "\n[Short ad copy]",
            f"Upgrade today: {name}. {feat}. Limited stock - order now.",
            "\n[Email subject + body]",
            f"Subject: {name} is here - don't miss out",
            f"Body: Hi there! We just restocked the {name}. {feat}. "
            "Shop now before it sells out. - The team",
        ])


def _hashtags(p: dict) -> str:
    words = []
    for kw in (p.get("keywords") or []):
        words.append("#" + str(kw).replace(" ", ""))
    if p.get("category"):
        words.append("#" + str(p["category"]).replace(" ", ""))
    words += ["#shopnow", "#deal"]
    return " ".join(words[:6])
