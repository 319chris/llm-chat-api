from __future__ import annotations

import os
import json
from typing import List, Dict, Callable, Optional
import httpx

from src.errors import UpstreamError, ConfigError
from src.llm.base import LLMResponse
from src.secrets import get_secret_value


class OpenAIClient:
    """
    Default provider: OpenAI-compatible Chat Completions API.

    Env vars (Lambda):
      - OPENAI_API_KEY_SECRET_ID: Secrets Manager secret name or ARN (required)
      - OPENAI_BASE_URL: default https://api.openai.com/v1
      - OPENAI_MODEL: default gpt-4o-mini
      - OPENAI_TIMEOUT_S: default 20
    """

    def __init__(
        self,
        secret_id: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_s: Optional[float] = None,
        http_client: Optional[httpx.Client] = None,
        secret_provider: Callable[[str], str] = get_secret_value,
    ) -> None:
        self.secret_id = secret_id or os.environ.get("OPENAI_API_KEY_SECRET_ID", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_s = float(timeout_s or os.environ.get("OPENAI_TIMEOUT_S", "20"))

        if not self.secret_id:
            raise ConfigError("Missing OPENAI_API_KEY_SECRET_ID environment variable")

        self._secret_provider = secret_provider
        self._http = http_client or httpx.Client(timeout=self.timeout_s)

    def _get_api_key(self) -> str:
        try:
            key = self._secret_provider(self.secret_id)
        except Exception as e:
            # Do not leak secret id or value
            raise ConfigError("Failed to load OpenAI API key from Secrets Manager") from e

        if not key or not key.strip():
            raise ConfigError("OpenAI API key is empty in Secrets Manager")
        return key.strip()

    def generate(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> LLMResponse:
        api_key = self._get_api_key()
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = self._http.post(url, headers=headers, content=json.dumps(payload).encode("utf-8"))
        except httpx.RequestError as e:
            raise UpstreamError("Failed to reach LLM provider") from e

        if resp.status_code < 200 or resp.status_code >= 300:
            # Never include resp.text if it could contain sensitive info; keep it minimal
            raise UpstreamError(f"LLM provider returned {resp.status_code}", status_code=502)

        try:
            data = resp.json()
        except ValueError as e:
            raise UpstreamError("LLM provider returned invalid JSON") from e

        rid = data.get("id", "")
        model = data.get("model", self.model)
        choices = data.get("choices") or []
        content = ""
        if choices and isinstance(choices, list):
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict):
                content = (msg.get("content") or "").strip()

        usage_raw = data.get("usage") or {}
        usage = {
            "prompt_tokens": int(usage_raw.get("prompt_tokens") or 0),
            "completion_tokens": int(usage_raw.get("completion_tokens") or 0),
            "total_tokens": int(usage_raw.get("total_tokens") or 0),
        }

        return LLMResponse(
            id=rid or "unknown",
            model=model,
            content=content,
            usage=usage,
        )