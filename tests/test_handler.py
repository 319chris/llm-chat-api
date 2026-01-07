import json
from src.handler import lambda_handler
from tests.conftest import make_apigw_v2_event


class FakeLLMClient:
    def generate(self, messages, temperature, max_tokens):
        return type(
            "LLMResponse",
            (),
            {
                "id": "chatcmpl_test",
                "model": "gpt-test",
                "content": "hello!",
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            },
        )()


def test_handler_success_structure(lambda_context, monkeypatch):
    # Patch the factory to avoid real provider calls
    import src.llm

    monkeypatch.setattr(src.llm, "get_llm_client", lambda: FakeLLMClient())

    event = make_apigw_v2_event(
        {"messages": [{"role": "user", "content": "hi"}], "temperature": 0.2, "max_tokens": 16}
    )
    resp = lambda_handler(event, lambda_context)

    assert resp["statusCode"] == 200
    assert resp["headers"]["Content-Type"] == "application/json"

    body = json.loads(resp["body"])
    assert "id" in body
    assert "model" in body
    assert "content" in body
    assert "usage" in body
    assert "latency_ms" in body
    assert body["content"] == "hello!"