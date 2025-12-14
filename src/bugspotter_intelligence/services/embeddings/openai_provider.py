import logging
from openai import OpenAI
from .base import EmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI embedding provider

    Uses OpenAI's text-embedding models
    Requires API key and costs money per token
    """

    DEFAULT_MODEL = "text-embedding-3-small"  # 1536 dimensions, cheaper

    # Alternative: "text-embedding-3-large"  # 3072 dimensions, more expensive

    def __init__(self, api_key: str, model_name: str | None = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized OpenAI embedding provider: {self.model_name}")

    def embed(self, text: str) -> list[float]:
        """Generate embedding using OpenAI API"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        logger.debug(f"Calling OpenAI API for embedding (length: {len(text)} chars)")

        response = self.client.embeddings.create(
            input=text,
            model=self.model_name
        )

        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            raise ValueError("Texts list cannot be empty")

        logger.debug(f"Calling OpenAI API for {len(texts)} embeddings")

        response = self.client.embeddings.create(
            input=texts,
            model=self.model_name
        )

        return [item.embedding for item in response.data]

    def dimension(self) -> int:
        """Get embedding dimension"""
        # text-embedding-3-small: 1536
        # text-embedding-3-large: 3072
        if "large" in self.model_name:
            return 3072
        return 1536

    @property
    def provider_name(self) -> str:
        return "openai"