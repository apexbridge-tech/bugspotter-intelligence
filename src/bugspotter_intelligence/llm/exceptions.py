"""LLM provider exceptions."""


class LLMBackendUnavailableError(Exception):
    """The configured LLM backend (Ollama / Claude / OpenAI) is unreachable or
    returned a transient server error.

    This is a dependency being down, not an internal defect - the API layer maps
    it to HTTP 503 (see api/error_handlers.py) so callers can degrade gracefully
    and retry, instead of treating it as a hard 500.
    """
