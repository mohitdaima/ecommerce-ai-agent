"""
Base Agent class. Every specialist (Listing, Pricing, ...) inherits this.

An agent has:
  * a name + role + emoji personality (so "meeting" them feels natural)
  * access to the shared LLM brain, the data store and business config
  * a `handle(task, product)` method returning text output

Subclasses implement `_system_prompt`, `_build_prompt` and `_fallback`.
The base `handle` wires the LLM in, and uses the free template fallback
when the local model is unavailable.
"""

from __future__ import annotations

from core.llm import LLM
from core.store import Store


class Agent:
    name: str = "Agent"
    role: str = "Generic agent"
    emoji: str = "*"

    def __init__(self, llm: LLM, store: Store, config: dict):
        self.llm = llm
        self.store = store
        self.config = config
        self.business = config.get("business", {})

    # -- to be overridden ----------------------------------------------
    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role} for an e-commerce business "
            f"named '{self.business.get('name', 'the store')}'. "
            f"Tone: {self.business.get('tone', 'professional')}. "
            f"Be concise, practical and ready-to-use.{self._language_clause()}"
        )

    def _language_clause(self) -> str:
        """Instruction so the LLM writes in the owner's chosen language."""
        lang = str(self.business.get("language", "english")).lower()
        if lang == "hindi":
            return (" Write your output in Hindi (Devanagari script), suitable "
                    "for Indian customers.")
        if lang == "hinglish":
            return (" Write your output in Hinglish - a natural mix of Hindi and "
                    "English written in Roman/English letters, the way popular "
                    "Indian brands write on social media.")
        return ""

    @property
    def language(self) -> str:
        return str(self.business.get("language", "english")).lower()

    def _build_prompt(self, task: str, product: dict | None) -> str:
        base = f"Task from the business owner: {task}\n"
        if product:
            base += f"\nProduct details:\n{self._format_product(product)}\n"
        base += "\nRespond with clear, ready-to-use output."
        return base

    def _fallback(self, task: str, product: dict | None) -> str:
        """Template output used when the local AI model is offline."""
        return (
            f"[{self.name} - offline template]\n"
            f"Task: {task}\n"
            "(Install Ollama + run `ollama pull llama3.2` for smart AI output.)"
        )

    # -- shared helpers -------------------------------------------------
    @staticmethod
    def _format_product(p: dict) -> str:
        lines = []
        for key in ("id", "name", "category", "price", "cost", "stock",
                    "features", "keywords", "description"):
            if key in p and p[key] not in (None, "", []):
                val = p[key]
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                lines.append(f"  - {key}: {val}")
        return "\n".join(lines)

    @property
    def channels(self) -> list[str]:
        return self.business.get("channels", [])

    # -- main entry -----------------------------------------------------
    def handle(self, task: str, product: dict | None = None) -> str:
        text = self.llm.generate(self._system_prompt(), self._build_prompt(task, product))
        if not text:
            text = self._fallback(task, product)
        # persist the work
        self.store.add_output(
            agent=self.name,
            title=task[:80],
            content=text,
            product_id=product["id"] if product else None,
        )
        return text
