import pytest
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm import (
    create_llm_provider,
    list_providers,
    OllamaProvider
)


class TestLLMFactory:
    """Test suite for LLM factory and registry"""

    def test_list_providers(self):
        """Test listing registered providers"""
        providers = list_providers()
        assert isinstance(providers, list)
        assert "ollama" in providers

    def test_create_ollama_provider(self):
        """Test creating Ollama provider"""
        settings = Settings()
        settings.llm_provider = "ollama"

        provider = create_llm_provider(settings)
        assert isinstance(provider, OllamaProvider)

    def test_invalid_provider(self):
        """Test error for invalid provider"""
        settings = Settings()
        settings.llm_provider = "nonexistent"

        with pytest.raises(ValueError) as exc_info:
            create_llm_provider(settings)

        assert "nonexistent" in str(exc_info.value)
        assert "Available providers" in str(exc_info.value)