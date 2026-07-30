"""Tests for the API exception handlers."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bugspotter_intelligence.api.error_handlers import llm_unavailable_handler
from bugspotter_intelligence.llm.exceptions import LLMBackendUnavailableError


def _app_with_handler() -> FastAPI:
    """Minimal app wired with the real handler, so we test the actual mapping
    without constructing the full application."""
    app = FastAPI()
    app.add_exception_handler(LLMBackendUnavailableError, llm_unavailable_handler)

    @app.get("/boom")
    async def boom():
        raise LLMBackendUnavailableError("ollama unreachable")

    return app


def test_llm_unavailable_maps_to_503():
    client = TestClient(_app_with_handler(), raise_server_exceptions=False)
    resp = client.get("/boom")

    assert resp.status_code == 503
    body = resp.json()
    assert body["detail"] == "LLM backend unavailable"
    assert body["code"] == "llm_unavailable"
    assert resp.headers.get("Retry-After") == "30"
