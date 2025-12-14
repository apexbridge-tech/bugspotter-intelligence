import logging
from bugspotter_intelligence.config import Settings
from .base import EmbeddingProvider
from .local import LocalEmbeddingProvider

logger = logging.getLogger(__name__)


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    """
    Create embedding provider based on settings

    Provider types:
    - local: sentence-transformers (self-hosted)
    - openai: OpenAI API
    - anthropic: Voyage AI via Anthropic
    """
    provider_type = settings.embedding_provider.lower()

    logger.info(f"Creating embedding provider: {provider_type}")

    if provider_type == "local":
        return LocalEmbeddingProvider(
            model_name=getattr(settings, "embedding_model", None)
        )

    if provider_type == "openai":
        from .openai_provider import OpenAIEmbeddingProvider

        if not settings.openai_api_key:
            raise ValueError("OpenAI API key required for OpenAI embedding provider")

        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model_name=getattr(settings, "embedding_model", None)
        )

    raise ValueError(
        f"Unsupported embedding provider: '{provider_type}'. "
        f"Supported: local, openai"
    )