import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from logging_config import set_request_id, get_logger

logger = get_logger("middleware.request_id")

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    - Reads X-Request-Id from the incoming request if present
    - Otherwise generates a new UUID
    - Stores it in a ContextVar so all logs in this request can use it
    - Adds it back to the response headers
    """

    async def dispatch(self, request, call_next):
        # 1) Get or generate request_id
        incoming = request.headers.get("x-request-id")
        request_id = incoming or str(uuid.uuid4())

        # 2) Store in ContextVar (used by logging filter)
        set_request_id(request_id)

        logger.info(f"➡️ Incoming request {request.method} {request.url.path}")

        # 3) Call route handler
        response = await call_next(request)

        # 4) Add it to response so clients can see / propagate it
        response.headers["x-request-id"] = request_id

        logger.info(f"⬅️ Completed request {request.method} {request.url.path} with status {response.status_code}")

        return response