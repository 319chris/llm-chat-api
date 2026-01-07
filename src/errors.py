from dataclasses import dataclass
from typing import Optional


@dataclass
class AppError(Exception):
    status_code: int
    error_type: str
    message: str
    details: Optional[dict] = None


class UpstreamError(AppError):
    def __init__(self, message: str, status_code: int = 502, details: Optional[dict] = None):
        super().__init__(status_code=status_code, error_type="upstream_error", message=message, details=details)


class ConfigError(AppError):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(status_code=500, error_type="config_error", message=message, details=details)
        