import json
import types
import pytest


@pytest.fixture
def lambda_context():
    # Minimal Lambda context stub
    return types.SimpleNamespace(aws_request_id="test-aws-request-id")


def make_apigw_v2_event(body: dict, is_b64: bool = False):
    raw = json.dumps(body)
    return {
        "version": "2.0",
        "routeKey": "POST /chat",
        "rawPath": "/chat",
        "headers": {"content-type": "application/json"},
        "requestContext": {
            "requestId": "test-request-id",
            "http": {"method": "POST", "path": "/chat"},
        },
        "isBase64Encoded": is_b64,
        "body": raw,
    }