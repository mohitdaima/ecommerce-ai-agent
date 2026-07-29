"""Marketing Agent - social posts, ad copy, emails, hashtags.

India-aware: supports festival campaigns (Diwali, Big Billion Days, etc.) and
writes in English, Hindi or Hinglish based on config.
"""

from __future__ import annotations

from core.agent import Agent

# Indian festival / sale events -> a marketing angle + hashtags.
FESTIVALS = {
    "diwali":   ("Diwali", "Roshni wala offer! Light up Diwali with", "#Diwali #DiwaliSale #FestiveVibes"),
    "holi":     ("Holi", "Add color to your Holi with", "#Holi #HoliVibes #FestivalOfColors"),
    "rakhi":    ("Raksha Bandhan", "Perfect Rakhi gift -", "#RakshaBandhan #Rakhi #GiftForSibling"),
    "raksha":   ("Raksha Bandhan", "Perfect Rakhi gift -", "#RakshaBandhan #Rakhi #GiftForSibling"),
    "big billion": ("Flipkart Big Billion Days", "Big Billion Days blockbuster deal on", "#BigBillionDays #Flipkart #MegaSale"),
    "great indian": ("Amazon Great Indian Festival", "Great Indian Festival mega deal on", "#GreatIndianFestival #AmazonSale"),
    "eid":      ("Eid", "Eid Mubarak! Celebrate with", "#Eid #EidMubarak #FestiveOffer"),
    "navratri": ("Navratri", "Navratri special -", "#Navratri #FestiveShopping"),
    "new year": ("New Year", "New Year, new deal on", "#NewYear #NewYearSale"),
    "republic": ("Republic Day Sale", "Republic Day dhamaka on", "#RepublicDaySale #26January"),
    "independence": ("Independence Day Sale", "Freedom sale on", "#IndependenceDaySale #15August"),
}


class MarketingAgent(Agent):
    name = "Mara"
    role = "Marketing & Content Creator"
    emoji = "[MKTG]"
    keywords = ["marketing", "ad", "ads", "social", "instagram", "facebook",
                "tiktok", "email", "campaign", "promo", "promotion", "caption",
                "hashtag", "newsletter", "launch", "festival", "sale", "offer",
                "diwali", "holi", "rakhi", "eid", "navratri"]

    def _system_prompt(self) -> str:
        base = (
            f"You are {self.name}, the {self.role} for an Indian online seller. "
            f"You create scroll-stopping social captions (with hashtags), short "
            f"ad copy, and email drafts. Tone: {self.business.get('tone')}."
        )
        return base + self._language_clause()

    def _detect_festival(self, task: str):
        t = task.lower()
        for key, data in FESTIVALS.items():
            if key in t:
                return data
        return None

    def _fallback(self, task: str, product: dict | None) -> str:
        p = product or {}
        name = p.get("name", "our product")
        feat = (p.get("features") or ["quality you can trust"])[0]
        fest = self._detect_festival(task)
        tags = _hashtags(p, fest)

        if fest:
            fest_name, angle, _ = fest
            header = f"=== {fest_name.upper()} MARKETING KIT for {name} ==="
            hook = f"{angle} {name} - {feat}."
        else:
            header = f"=== MARKETING KIT for {name} ==="
            hook = f"Meet the {name} - {feat}."

        lang = self.language
        if lang == "hinglish":
            caption = f"{hook} Abhi order karo aur dekho kyun sab isse pasand karte hain! Limited stock! {tags}"
            ad = f"Aaj hi le aao: {name}. {feat}. Stock kam hai - jaldi karo!"
            email_sub = f"{name} aa gaya hai - miss mat karna!"
            email_body = (f"Namaste! {name} ab available hai. {feat}. "
                          f"Sold out hone se pehle order karein. - Team")
        elif lang == "hindi":
            caption = f"{hook} \u0905\u092d\u0940 \u0911\u0930\u094d\u0921\u0930 \u0915\u0930\u0947\u0902! {tags}"
            ad = f"\u0906\u091c \u0939\u0940 \u0916\u0930\u0940\u0926\u0947\u0902: {name}\u0964 {feat}\u0964"
            email_sub = f"{name} \u0905\u092c \u0909\u092a\u0932\u092c\u094d\u0927 \u0939\u0948"
            email_body = (f"\u0928\u092e\u0938\u094d\u0924\u0947! {name} \u0905\u092c \u0909\u092a\u0932\u092c\u094d\u0927 \u0939\u0948\u0964 {feat}\u0964 - \u091f\u0940\u092e")
        else:
            caption = f"{hook} Tap to shop and see why customers love it! {tags}"
            ad = f"Upgrade today: {name}. {feat}. Limited stock - order now."
            email_sub = f"{name} is here - don't miss out"
            email_body = (f"Hi there! We just restocked the {name}. {feat}. "
                          f"Shop now before it sells out. - The team")

        return "\n".join([
            header,
            "\n[Instagram / Facebook caption]", caption,
            "\n[Short ad copy]", ad,
            "\n[Email subject + body]",
            f"Subject: {email_sub}", f"Body: {email_body}",
        ])


def _hashtags(p: dict, fest=None) -> str:
    words = []
    for kw in (p.get("keywords") or []):
        words.append("#" + str(kw).replace(" ", ""))
    if p.get("category"):
        words.append("#" + str(p["category"]).replace(" ", ""))
    words += ["#ShopNow", "#India", "#OnlineShopping"]
    tags = " ".join(dict.fromkeys(words[:6]))
    if fest:
        tags = fest[2] + " " + tags
    return tags
