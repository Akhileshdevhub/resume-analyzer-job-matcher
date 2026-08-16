"""Provider-agnostic LLM client.

One thin wrapper over whichever provider is configured (OpenAI or Anthropic),
so the rest of the app never imports a vendor SDK or hard-codes an endpoint. We
call the HTTP APIs directly with `httpx` to keep dependencies minimal and the
provider genuinely swappable.

Design points that matter in an interview:
  * The LLM is OPTIONAL. If no provider/key is configured, `is_enabled` is False
    and callers use deterministic templates instead — the app never hard-depends
    on an external API.
  * Every call is time-boxed and wrapped: any failure raises `LLMError`, which
    callers catch and fall back from. A flaky LLM can never take down a request.
  * `generate_json` asks for and parses strict JSON, so downstream code gets
    structured data, not free text.
"""
from __future__ import annotations

import json

import httpx

from ..core.config import get_settings
from ..core.errors import LLMError
from ..core.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self) -> None:
        s = get_settings()
        self.provider = s.llm_provider.strip().lower()
        self.model = s.llm_model.strip()
        self.api_key = s.llm_api_key.strip()
        self.timeout = s.llm_timeout_seconds
        self.enabled = s.llm_enabled

    @property
    def is_enabled(self) -> bool:
        return self.enabled

    # -- public API -----------------------------------------------------------
    def generate(self, system: str, user: str, max_tokens: int = 800) -> str:
        """Return the model's text response. Raises LLMError on any failure."""
        if not self.enabled:
            raise LLMError("LLM is not configured.")
        try:
            if self.provider == "openai":
                return self._call_openai(system, user, max_tokens)
            if self.provider == "anthropic":
                return self._call_anthropic(system, user, max_tokens)
            raise LLMError(f"Unknown LLM provider: {self.provider!r}")
        except LLMError:
            raise
        except httpx.TimeoutException as exc:
            raise LLMError(f"LLM request timed out after {self.timeout}s") from exc
        except Exception as exc:  # network, auth, malformed response, ...
            raise LLMError(f"LLM request failed: {exc}") from exc

    def generate_json(self, system: str, user: str, max_tokens: int = 800) -> dict:
        """Generate and parse a JSON object. Raises LLMError if it isn't valid JSON."""
        text = self.generate(system + "\nRespond with ONLY valid JSON.", user, max_tokens)
        return _extract_json(text)

    # -- providers ------------------------------------------------------------
    def _call_openai(self, system: str, user: str, max_tokens: int) -> str:
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model or "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.3,
                "max_tokens": max_tokens,
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_anthropic(self, system: str, user: str, max_tokens: int) -> str:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model or "claude-3-5-haiku-latest",
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a text response and parse it.

    LLMs sometimes wrap JSON in prose or ```json fences, so we locate the outer
    braces rather than trusting the whole string to be clean JSON.
    """
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise LLMError("LLM response did not contain a JSON object.")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError(f"LLM returned invalid JSON: {exc}") from exc


def get_llm_client() -> LLMClient:
    return LLMClient()
