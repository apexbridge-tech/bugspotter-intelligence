"""Abstract base class for embedding providers"""

from abc import ABC, abstractmethod

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text"""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts"""
        pass

    @abstractmethod
    def dimension(self) -> int:
        """Get the embedding dimension"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name"""
        pass