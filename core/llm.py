"""
Local LLM client - the free "brain" of the agents.

Design goals:
  * 100% FREE. Uses Ollama running on your own machine (no API credits).
  * Never hard-crash. If Ollama is not installed or not running, we
    gracefully fall back to deterministic templates so every agent still
    produces useful output.

Install the free brain (one time):
  1. Download Ollama:  https://ollama.com/download
  2. Pull a free model: `ollama pull llama3.2`
  3. That's it - Ollama serves it at http://localhost:11434
"""

from __future__ import annotations

import json
from typing import Optional

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


class LLM:
    """Thin wrapper around a local Ollama server with a safe fallback."""

    def __init__(self, config: dict):
        llm_cfg = config.get("llm", {})
        self.host: str = llm_cfg.get("host", "http://localhost:11434")
        self.model: str = llm_cfg.get("model", "llama3.2")
        self.temperature: float = float(llm_cfg.get("temperature", 0.7))
        self.timeout: int = int(llm_cfg.get("timeout_seconds", 120))
        self.fallback: bool = bool(llm_cfg.get("fallback_to_templates", True))
        self._available: Optional[bool] = None  # cached availability

    # -- availability ---------------------------------------------------
    def is_available(self) -> bool:
        """Check (once) whether a local Ollama server is reachable."""
        if self._available is not None:
            return self._available
        if requests is None:
            self._available = False
            return False
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=3)
            self._available = resp.status_code == 200
        except Exception:
            self._available = False
        return self._available

    # -- generation -----------------------------------------------------
    def generate(self, system: str, prompt: str) -> str:
        """
        Ask the local model to respond. Returns text.
        If the model is unreachable, returns "" so callers can use a
        template fallback instead.
        """
        if not self.is_available():
            return ""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": self.temperature},
            }
            resp = requests.post(
                f"{self.host}/api/generate",
                data=json.dumps(payload),
                timeout=self.timeout,
            )
            if resp.status_code != 200:
                return ""
            return resp.json().get("response", "").strip()
        except Exception:
            return ""

    def status_line(self) -> str:
        if self.is_available():
            return f"AI brain: Ollama ONLINE (model: {self.model}) - free & local"
        return "AI brain: Ollama offline -> using free built-in templates"
