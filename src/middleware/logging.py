import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    return request_id_var.get()


class JSONLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "request_id": getattr(record, "request_id", "no-request-id"),
            "event": getattr(record, "event", "unknown"),
            "duration_ms": getattr(record, "duration_ms", None),
        }
        sys.stdout.write(json.dumps(log_entry) + "\n")
        sys.stdout.flush()


def setup_logging():
    handler = JSONLogHandler()
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        setup_logging()
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request_id_var.set(request_id)

        logger = logging.getLogger("middleware")
        logger.info(
            "request_received",
            extra={
                "event": "request_received",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": None,
            },
        )

        response: Response = await call_next(request)
        response.headers["x-request-id"] = request_id

        logger.info(
            "response_sent",
            extra={
                "event": "response_sent",
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": None,
            },
        )
        return response