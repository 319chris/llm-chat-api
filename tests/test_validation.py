import json
from src.handler import lambda_handler
from tests.conftest import make_apigw_v2_event


def test_empty_messages_returns_400(lambda_context):
    event = make_apigw_v2_event({"messages": [], "temperature": 0.2, "max_tokens": 16})
    resp = lambda_handler(event, lambda_context)
    assert resp["statusCode"] == 400
    body = json.loads(resp["body"])
    assert body["error"]["type"] == "validation_error"


def test_invalid_role_returns_400(lambda_context):
    event = make_apigw_v2_event(
        {"messages": [{"role": "dev", "content": "hi"}], "temperature": 0.2, "max_tokens": 16}
    )
    resp = lambda_handler(event, lambda_context)
    assert resp["statusCode"] == 400
    body = json.loads(resp["body"])
    assert body["error"]["type"] == "validation_error"


def test_empty_content_returns_400(lambda_context):
    event = make_apigw_v2_event(
        {"messages": [{"role": "user", "content": "   "}], "temperature": 0.2, "max_tokens": 16}
    )
    resp = lambda_handler(event, lambda_context)
    assert resp["statusCode"] == 400
    body = json.loads(resp["body"])
    assert body["error"]["type"] == "validation_error"