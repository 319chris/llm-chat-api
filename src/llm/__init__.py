import os
from src.errors import ConfigError
from src.llm.openai_client import OpenAIClient

# Phase 2 expansion point:
# - Add Bedrock client implementing same generate() signature
# - Switch by env var LLM_PROVIDER=bedrock

def get_llm_client():
    provider = os.environ.get("LLM_PROVIDER", "openai").lower().strip()

    if provider == "openai":
        return OpenAIClient()

    # Placeholder for Phase 2 (not implemented)
    if provider == "bedrock":
        raise ConfigError("Bedrock provider is not implemented in Phase 1 (reserved for Phase 2)")

    raise ConfigError(f"Unknown LLM provider: {provider}")