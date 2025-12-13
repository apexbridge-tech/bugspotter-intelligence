import pytest
from unittest.mock import AsyncMock, patch
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm.ollama import OllamaProvider


@pytest.fixture
def settings():
    """Fixture for test settings"""
    return Settings()


@pytest.fixture
def ollama_provider(settings):
    """Fixture for OllamaProvider instance"""
    return OllamaProvider(settings)


class TestOllamaProvider:
    """Test suite for OllamaProvider"""

    def test_initialization(self, ollama_provider, settings):
        """Test provider initializes correctly"""
        assert ollama_provider.settings == settings
        assert ollama_provider.API_TIMEOUT == 180.0

    @pytest.mark.asyncio
    async def test_generate_simple(self, ollama_provider):
        """Test simple generation without context"""
        response = await ollama_provider.generate(
            prompt="Say hello in one word",
            max_tokens=10
        )

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_generate_with_context(self, ollama_provider):
        """Test generation with context"""
        context = [
            "Bug #1: Null pointer in login",
            "Bug #2: Crash on empty input"
        ]

        response = await ollama_provider.generate(
            prompt="What's the common issue?",
            context=context,
            max_tokens=50
        )

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, ollama_provider):
        """Test error handling for API failures"""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock a 500 error
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = Exception("Server error")
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                await ollama_provider.generate("test")