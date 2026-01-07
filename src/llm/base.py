from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Protocol


@dataclass
class LLMResponse:
    id: str
    model: str
    content: str
    usage: Dict[str, int]


class BaseLLMClient(Protocol):
    def generate(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> LLMResponse:
        ...
        