import json
import httpx
import pytest

from src.llm.openai_client import OpenAIClient
from src.errors import UpstreamError


def test_openai_client_calls_chat_completions_and_parses_response():
    captured = {}

    def secret_provider(_secret_id: str) -> str:
        return "sk-test-do-not-log"

    def transport_handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        payload = json.loads(request.content.decode("utf-8"))
        captured["payload"] = payload

        return httpx.Response(
            200,
            json={
                "id": "chatcmpl_123",
                "model": "gpt-test",
                "choices": [{"message": {"role": "assistant", "content": "OK"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(transport_handler), timeout=5)

    c = OpenAIClient(
        secret_id="arn:aws:secretsmanager:ap-southeast-2:<ACCOUNT_ID>:secret:/llm-chat-api/openai_api_key-xxxx",
        base_url="https://api.openai.com/v1",
        model="gpt-test",
        http_client=client,
        secret_provider=secret_provider,
    )

    resp = c.generate(messages=[{"role": "user", "content": "hi"}], temperature=0.2, max_tokens=16)
    assert resp.id == "chatcmpl_123"
    assert resp.model == "gpt-test"
    assert resp.content == "OK"
    assert resp.usage["total_tokens"] == 12

    assert captured["url"].endswith("/chat/completions")
    assert captured["auth"] == "Bearer sk-test-do-not-log"
    assert captured["payload"]["messages"][0]["role"] == "user"


def test_openai_client_upstream_error_does_not_leak_secret():
    def secret_provider(_secret_id: str) -> str:
        return "sk-super-secret"

    def transport_handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "unauthorized"}})

    client = httpx.Client(transport=httpx.MockTransport(transport_handler), timeout=5)

    c = OpenAIClient(
        secret_id="dummy",
        http_client=client,
        secret_provider=secret_provider,
    )

    with pytest.raises(UpstreamError) as e:
        c.generate(messages=[{"role": "user", "content": "hi"}], temperature=0.2, max_tokens=16)

    # Ensure exception message does not contain secret
    assert "sk-super-secret" not in str(e.value)