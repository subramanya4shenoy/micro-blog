import logging
import sys
import uuid
from contextvars import ContextVar

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)

def get_request_id() -> str | None:
    return _request_id_ctx.get()

class RequestIdFilter(logging.Filter):
    """Injects req id in every log record"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True

def setup_logging() -> None:
    """
    Configure a dedicated 'microblog' logger with structured-ish output.
    Call this once in main.py.
    """
    logger = logging.getLogger("microblog")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s | level=%(levelname)s | logger=%(name)s | request_id=%(request_id)s | %(message)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    logger.addHandler(handler)


def get_logger(name: str | None = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"microblog.{name}")
    return logging.getLogger("microblog")
 
