from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, conlist, confloat, conint

Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    role: Role
    content: str = Field(..., description="Message content")

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if v is None:
            raise ValueError("content is required")
        vv = v.strip()
        if not vv:
            raise ValueError("content must not be empty")
        return vv


class ChatRequest(BaseModel):
    messages: conlist(Message, min_length=1)  # type: ignore[valid-type]
    temperature: confloat(ge=0.0, le=2.0) = 0.2  # type: ignore[valid-type]
    max_tokens: conint(ge=1, le=4096) = 512  # type: ignore[valid-type]


class ErrorResponse(BaseModel):
    error: Dict[str, Any]
    request_id: Optional[str] = None
    