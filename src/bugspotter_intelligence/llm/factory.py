from typing import Type, Dict
from bugspotter_intelligence.config import Settings
from .base import LLMProvider

# Registry of available providers
_PROVIDER_REGISTRY: Dict[str, Type[LLMProvider]] = {}


def register_provider(name: str):
    """
    Decorator to register an LLM provider

    Usage:
        @register_provider("ollama")
        class OllamaProvider(LLMProvider):
            ...

    Args:
        name: Provider name (e.g., "ollama", "claude", "openai")
    """

    def decorator(cls: Type[LLMProvider]):
        _PROVIDER_REGISTRY[name.lower()] = cls
        return cls

    return decorator


def create_llm_provider(settings: Settings) -> LLMProvider:
    """
    Factory function to create LLM provider based on settings

    Args:
        settings: Application settings

    Returns:
        Configured LLM provider instance

    Raises:
        ValueError: If provider type is not supported
    """
    provider_type = settings.llm_provider.lower()

    provider_class = _PROVIDER_REGISTRY.get(provider_type)

    if provider_class is None:
        available = ", ".join(_PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported LLM provider: '{provider_type}'. "
            f"Available providers: {available}"
        )

    return provider_class(settings)


def list_providers() -> list[str]:
    """Return list of registered provider names"""
    return list(_PROVIDER_REGISTRY.keys())