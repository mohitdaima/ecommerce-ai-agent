"""
Returns Agent - tracks returns/RMAs across marketplaces and manages the flow.

Reggie logs return requests, tracks their status (requested -> approved ->
received -> refunded -> closed), drafts the customer message for the return,
optionally restocks inventory when an item comes back sellable, and reports on
return trends so you can spot problem products.

Talk to it naturally, e.g.:
  "log a return for the bamboo mug on Amazon, reason: arrived damaged"
  "show me all open returns"
  "mark RMA-AB12CD as refunded"
  "which product gets returned the most?"
"""

from __future__ import annotations

import re

from core.agent import Agent

# words that hint at a returned item being resellable -> can restock
RESTOCKABLE_HINTS = ["changed mind", "wrong size", "didn't like", "did not like",
                     "no longer needed", "too big", "too small", "unwanted"]
# words that mean the item is NOT resellable -> do not restock
DAMAGED_HINTS = ["damaged", "broken", "defective", "faulty", "used", "opened",
                 "not working", "doesn't work"]


class ReturnsAgent(Agent):
    name = "Reggie"
    role = "Returns & RMA Manager"
    emoji = "[RTN]"
    keywords = ["return", "returns", "rma", "refund", "exchange",
                "send back", "sent back", "money back", "give back"]

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, the {self.role}. You handle product returns "
            f"professionally: log the RMA, guide the customer, decide if the item "
            f"can be restocked, and keep clear records. Tone: "
            f"{self.business.get('tone')}."
        )

    # Returns is data + workflow driven, so we handle it directly (works
    # offline). The LLM only adds an optional friendly customer message.
    def handle(self, task: str, product: dict | None = None) -> str:
        t = task.lower()

        # 1) status update:  "mark RMA-XXXXXX as refunded"
        rma_match = re.search(r"(rma-[a-z0-9]{6})", t)
        status_word = self._detect_status(t)
        if rma_match and status_word and ("mark" in t or "update" in t
                                          or "set" in t or "as " in t):
            updated = self.store.update_return(rma_match.group(1), status_word)
            if updated:
                # restock if it came back sellable and is now received/closed
                self._maybe_restock(updated)
                text = (f"Updated {updated['rma']} -> status: {status_word}.\n"
                        + self._one_line(updated))
            else:
                text = f"I couldn't find {rma_match.group(1).upper()}."
            return self._record(task, product, text)

        # 2) list / report:  "show open returns", "which product returns most"
        if any(w in t for w in ["show", "list", "all open", "report", "which",
                                "most", "trend", "how many"]):
            return self._record(task, product, self._report(t))

        # 3) otherwise: log a NEW return
        return self._record(task, product, self._log_new(task, product))

    # -- helpers --------------------------------------------------------
    def _detect_status(self, t: str) -> str | None:
        for s in ("refunded", "received", "approved", "closed", "requested"):
            if s in t:
                return s
        return None

    def _detect_channel(self, t: str) -> str:
        t_low = t.lower()
        for ch in self.channels:
            if ch.lower() in t_low:
                return ch
        return "unknown"

    def _extract_reason(self, task: str) -> str:
        m = re.search(r"reason[:\-]?\s*(.+)$", task, re.IGNORECASE)
        if m:
            return m.group(1).strip().rstrip(".")
        # fallback: look for known hint words
        low = task.lower()
        for hint in DAMAGED_HINTS + RESTOCKABLE_HINTS:
            if hint in low:
                return hint
        return "not specified"

    def _is_restockable(self, reason: str) -> bool:
        low = reason.lower()
        if any(h in low for h in DAMAGED_HINTS):
            return False
        if any(h in low for h in RESTOCKABLE_HINTS):
            return True
        return False  # default to safe: don't auto-restock unknown reasons

    def _log_new(self, task: str, product: dict | None) -> str:
        reason = self._extract_reason(task)
        channel = self._detect_channel(task)
        restock = self._is_restockable(reason)
        pid = product["id"] if product else None
        pname = product["name"] if product else "unknown product"
        rma = self.store.add_return(pid, pname, channel, reason, restock=restock)

        msg = self._customer_message(pname, reason)
        return "\n".join([
            "=== RETURN LOGGED ===",
            f"RMA: {rma['rma']}",
            f"Product: {pname}",
            f"Channel: {channel}",
            f"Reason: {reason}",
            f"Restockable: {'yes (item can be resold)' if restock else 'no (inspect first / not resellable)'}",
            "Status: requested",
            "",
            "--- Draft message to customer ---",
            msg,
            "",
            f"Next: when the item arrives, say \"mark {rma['rma']} as received\", "
            f"then \"mark {rma['rma']} as refunded\".",
        ])

    def _customer_message(self, pname: str, reason: str) -> str:
        llm_msg = self.llm.generate(
            self._system_prompt(),
            f"Write a short, warm reply approving a return for '{pname}'. "
            f"Reason: {reason}. Tell them a prepaid label is attached and refund "
            f"is issued once we receive it. 3 sentences max.",
        )
        if llm_msg:
            return llm_msg
        return (f"Hi! Thanks for reaching out about your {pname}. I've approved "
                f"your return - a prepaid label is attached. As soon as it "
                f"arrives back with us, your refund will be issued. We're sorry "
                f"for any inconvenience!")

    def _maybe_restock(self, rma: dict) -> None:
        if (rma.get("restock") and rma["status"] in ("received", "closed")
                and rma.get("product_id")):
            p = self.store.get_product(rma["product_id"])
            if p and isinstance(p.get("stock"), (int, float)):
                self.store.update_stock(rma["product_id"], int(p["stock"]) + 1)

    def _report(self, t: str) -> str:
        rets = self.store.list_returns()
        if not rets:
            return "[Reggie] No returns logged yet. That's a good thing!"

        # "which product returned most" / trend view
        if any(w in t for w in ["which", "most", "trend"]):
            counts: dict[str, int] = {}
            for r in rets:
                counts[r["product_name"]] = counts.get(r["product_name"], 0) + 1
            ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            lines = ["=== RETURN TRENDS ==="]
            for name, c in ranked:
                lines.append(f"- {name}: {c} return(s)")
            top = ranked[0]
            if top[1] >= 3:
                lines.append(f"\nHeads up: '{top[0]}' is returned often - check "
                             f"its listing accuracy, sizing, or quality.")
            return "\n".join(lines)

        # open vs all
        open_only = "open" in t or "requested" in t
        shown = [r for r in rets
                 if not open_only or r["status"] not in ("refunded", "closed")]
        if not shown:
            return "[Reggie] No open returns - all resolved!"
        lines = ["=== RETURNS ===" if not open_only else "=== OPEN RETURNS ==="]
        for r in shown:
            lines.append(self._one_line(r))
        return "\n".join(lines)

    @staticmethod
    def _one_line(r: dict) -> str:
        return (f"- {r['rma']} | {r['product_name']} | {r['channel']} | "
                f"{r['reason']} | status: {r['status']}")

    def _record(self, task: str, product: dict | None, text: str) -> str:
        self.store.add_output(self.name, task[:80], text,
                              product["id"] if product else None)
        return text
