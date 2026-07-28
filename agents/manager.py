"""
Manager Agent - the team lead you "meet" with.

You talk to the Manager in plain English. It:
  1. Understands what you want.
  2. Picks the right specialist agent(s) (routing by intent/keywords, with an
     optional LLM assist).
  3. Delegates the task, collects the result, and reports back to you.
"""

from __future__ import annotations

from core.agent import Agent
from core.llm import LLM
from core.store import Store
from agents import SPECIALISTS


class Manager:
    name = "Max"
    role = "General Manager"
    emoji = "[BOSS]"

    def __init__(self, llm: LLM, store: Store, config: dict):
        self.llm = llm
        self.store = store
        self.config = config
        # instantiate the whole team
        self.team = {cls.name: cls(llm, store, config) for cls in SPECIALISTS}

    # -- routing --------------------------------------------------------
    def route(self, task: str) -> list[Agent]:
        """Choose which specialist(s) should handle a task."""
        task_l = task.lower()
        scored: list[tuple[int, Agent]] = []
        for agent in self.team.values():
            score = sum(1 for kw in getattr(agent, "keywords", [])
                        if kw in task_l)
            if score:
                scored.append((score, agent))
        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            top = scored[0][0]
            # allow ties (e.g. "list AND price this") to run together
            return [a for s, a in scored if s == top]
        # nothing matched -> ask the LLM to pick, else default to Listing
        chosen = self._llm_route(task)
        return [chosen] if chosen else [self.team["Livia"]]

    def _llm_route(self, task: str) -> Agent | None:
        if not self.llm.is_available():
            return None
        roster = "\n".join(f"- {a.name}: {a.role}" for a in self.team.values())
        answer = self.llm.generate(
            "You route e-commerce tasks to the right team member. "
            "Reply with ONLY the member's first name from the list.",
            f"Team:\n{roster}\n\nTask: {task}\n\nBest member name:",
        )
        for name, agent in self.team.items():
            if name.lower() in answer.lower():
                return agent
        return None

    # -- product resolution --------------------------------------------
    def resolve_product(self, task: str) -> dict | None:
        """If the task mentions a product name/id, attach it."""
        for p in self.store.list_products():
            if p["id"] in task or p.get("name", "").lower() in task.lower():
                return p
        products = self.store.list_products()
        return products[0] if len(products) == 1 else None

    # -- main entry -----------------------------------------------------
    def delegate(self, task: str, product: dict | None = None) -> dict:
        agents = self.route(task)
        if product is None:
            product = self.resolve_product(task)
        results = []
        for agent in agents:
            output = agent.handle(task, product)
            self.store.add_task(task, agent.name)
            results.append({"agent": agent, "output": output})
        return {
            "assigned": [f"{a['agent'].emoji} {a['agent'].name} "
                         f"({a['agent'].role})" for a in results],
            "product": product,
            "results": results,
        }

    def roster_text(self) -> str:
        lines = [f"{self.emoji} {self.name} - {self.role} (that's me!)"]
        for a in self.team.values():
            lines.append(f"{a.emoji} {a.name} - {a.role}")
        return "\n".join(lines)
