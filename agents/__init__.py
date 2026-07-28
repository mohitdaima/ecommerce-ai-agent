"""The AI team - one module per specialist agent."""

from agents.listing import ListingAgent
from agents.pricing import PricingAgent
from agents.marketing import MarketingAgent
from agents.support import SupportAgent
from agents.inventory import InventoryAgent
from agents.analytics import AnalyticsAgent
from agents.seo import SEOAgent
from agents.returns import ReturnsAgent

# Registry of every specialist (Manager is separate - it leads them).
SPECIALISTS = [
    ListingAgent,
    PricingAgent,
    MarketingAgent,
    SupportAgent,
    InventoryAgent,
    AnalyticsAgent,
    SEOAgent,
    ReturnsAgent,
]

__all__ = [
    "ListingAgent", "PricingAgent", "MarketingAgent", "SupportAgent",
    "InventoryAgent", "AnalyticsAgent", "SEOAgent", "ReturnsAgent",
    "SPECIALISTS",
]
