"""Support Agent - drafts customer service replies and FAQs."""

from __future__ import annotations

from core.agent import Agent


class SupportAgent(Agent):
    name = "Sam"
    role = "Customer Support Specialist"
    emoji = "[HELP]"
    keywords = ["support", "customer", "reply", "respond", "complaint",
                "faq", "question", "review", "message", "ticket",
                "shipping", "order status"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You write empathetic, "
            f"solution-oriented replies to customers, and clear FAQ answers. "
            f"Tone: {self.business.get('tone')}. Never make promises about "
            f"specifics you weren't told; ask for order numbers when needed."
        )

    def _fallback(self, task: str, product: dict | None) -> str:
        return "\n".join([
            "=== CUSTOMER REPLY DRAFT ===",
            "Hi there, thanks so much for reaching out! I'm sorry for any "
            "trouble and I'm happy to help.",
            "",
            f"Regarding your message: \"{task}\"",
            "",
            "Could you share your order number so I can look into this right "
            "away? We'll make sure you're taken care of. - Customer Care",
            "",
            "[FAQ suggestion] Consider adding this to your store FAQ:",
            "Q: What's your return policy?  A: Free returns within 30 days.",
        ])
