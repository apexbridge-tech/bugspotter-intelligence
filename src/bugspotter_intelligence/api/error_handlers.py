"""FastAPI exception handlers.

Kept in a small module so the mapping can be unit-tested against a minimal app
without constructing the full application.
"""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from bugspotter_intelligence.llm.exceptions import LLMBackendUnavailableError

logger = logging.getLogger(__name__)


async def llm_unavailable_handler(
    request: Request, exc: LLMBackendUnavailableError
) -> JSONResponse:
    """Map an unreachable LLM backend to 503 Service Unavailable.

    A down LLM dependency is transient and retryable, not an internal defect, so
    it must NOT surface as 500. The embedding/search layer is unaffected - only
    LLM-backed endpoints (ask, mitigation) hit this path.
    """
    logger.warning(
        "LLM backend unavailable on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=503,
        content={"detail": "LLM backend unavailable", "code": "llm_unavailable"},
        headers={"Retry-After": "30"},
    )
