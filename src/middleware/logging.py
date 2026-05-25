import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_request_id_context: str = ""


def get_request_id() -> str:
    return _request_id_context


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global _request_id_context
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        _request_id_context = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response