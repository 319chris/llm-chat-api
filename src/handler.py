import base64
import json
import time
from typing import Any, Dict, Optional, List

from aws_lambda_powertools import Logger
from pydantic import ValidationError

from src.models import ChatRequest
from src.errors import AppError, UpstreamError
import src.llm as llm  # <-- changed: import module, not function

logger = Logger(service="llm-chat-api")


def _json_response(status_code: int, payload: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
    body = payload
    if request_id is not None:
        body = {**payload, "request_id": request_id}

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


def _parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    raw = event.get("body")
    if raw is None:
        raise ValueError("Missing request body")

    if event.get("isBase64Encoded") is True:
        raw = base64.b64decode(raw).decode("utf-8")

    if not isinstance(raw, str):
        raise ValueError("Invalid request body type")

    return json.loads(raw)


def _safe_validation_details(e: ValidationError) -> List[Dict[str, Any]]:
    """
    Pydantic v2 ValidationError.errors() may contain non-JSON-serializable objects.
    Return a JSON-safe subset only.
    """
    details: List[Dict[str, Any]] = []
    for err in e.errors():
        details.append(
            {
                "loc": err.get("loc"),
                "msg": err.get("msg"),
                "type": err.get("type"),
            }
        )
    return details


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    start = time.perf_counter()

    request_id = None
    try:
        request_id = (
            (event.get("requestContext") or {}).get("requestId")
            or getattr(context, "aws_request_id", None)
        )
    except Exception:
        request_id = getattr(context, "aws_request_id", None)

    if request_id:
        logger.append_keys(request_id=request_id)

    try:
        data = _parse_event_body(event)
        req = ChatRequest.model_validate(data)

        messages = [{"role": m.role, "content": m.content} for m in req.messages]

        client = llm.get_llm_client()  # <-- changed: call via module
        llm_resp = client.generate(messages=messages, temperature=req.temperature, max_tokens=req.max_tokens)

        latency_ms = int((time.perf_counter() - start) * 1000)

        logger.info(
            "chat_success",
            latency_ms=latency_ms,
            model=llm_resp.model,
            usage=llm_resp.usage,
            message_count=len(messages),
        )

        return _json_response(
            200,
            {
                "id": llm_resp.id,
                "model": llm_resp.model,
                "content": llm_resp.content,
                "usage": llm_resp.usage,
                "latency_ms": latency_ms,
            },
            request_id=request_id,
        )

    except ValidationError as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.warning("validation_error", latency_ms=latency_ms)

        return _json_response(
            400,
            {
                "error": {
                    "type": "validation_error",
                    "message": "Invalid request body",
                    "details": _safe_validation_details(e),
                }
            },
            request_id=request_id,
        )

    except (ValueError, json.JSONDecodeError) as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.warning("bad_request", latency_ms=latency_ms)

        return _json_response(
            400,
            {
                "error": {
                    "type": "bad_request",
                    "message": str(e),
                }
            },
            request_id=request_id,
        )

    except UpstreamError as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.error("upstream_error", latency_ms=latency_ms)

        return _json_response(
            502,
            {
                "error": {
                    "type": e.error_type,
                    "message": e.message,
                }
            },
            request_id=request_id,
        )

    except AppError as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.error("app_error", latency_ms=latency_ms, error_type=e.error_type)

        return _json_response(
            e.status_code,
            {
                "error": {
                    "type": e.error_type,
                    "message": e.message,
                    "details": e.details,
                }
            },
            request_id=request_id,
        )

    except Exception:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.exception("internal_error", latency_ms=latency_ms)

        return _json_response(
            500,
            {
                "error": {
                    "type": "internal_error",
                    "message": "Internal server error",
                }
            },
            request_id=request_id,
        )