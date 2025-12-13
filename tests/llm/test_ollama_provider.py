import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm.ollama import OllamaProvider


@pytest.fixture
def settings():
    """Fixture for test settings (mocked tests)"""
    return Settings()


@pytest.fixture
def ollama_provider(settings):
    """Fixture for OllamaProvider instance (mocked tests)"""
    return OllamaProvider(settings)


class TestOllamaProviderUnit:
    """Unit tests (mocked, fast)"""

    def test_initialization(self, ollama_provider, settings):
        """Test provider initializes correctly"""
        assert ollama_provider.settings == settings
        assert ollama_provider.API_TIMEOUT == 120.0

    @pytest.mark.asyncio
    async def test_generate_simple_mocked(self, ollama_provider):
        """Test simple generation (mocked HTTP call)"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "Hello!"}

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            response = await ollama_provider.generate(
                prompt="Say hello",
                max_tokens=10
            )

            assert response == "Hello!"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_context_mocked(self, ollama_provider):
        """Test generation with context (mocked)"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "response": "The common issue is null pointer errors."
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

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
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            # Simulate raise_for_status raising an exception
            from httpx import HTTPStatusError, Request, Response
            mock_response.raise_for_status.side_effect = HTTPStatusError(
                "Server error",
                request=MagicMock(),
                response=mock_response
            )

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            with pytest.raises(Exception) as exc_info:
                await ollama_provider.generate("test")

            assert "500" in str(exc_info.value)


@pytest.mark.integration
class TestOllamaProviderIntegration:
    """Integration tests (real Ollama via testcontainers, slower)"""

    @pytest.mark.asyncio
    async def test_generate_simple_real(self, settings_with_testcontainer):
        """Test simple generation with real Ollama"""
        provider = OllamaProvider(settings_with_testcontainer)

        response = await provider.generate(
            prompt="Say hello in 5 words or less",
            max_tokens=20,
            temperature=0.1  # Low temperature for consistency
        )

        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\nOllama response: {response}")

    @pytest.mark.asyncio
    async def test_generate_with_context_real(self, settings_with_testcontainer):
        """Test generation with context using real Ollama"""
        provider = OllamaProvider(settings_with_testcontainer)

        context = [
            "Bug #1: Application crashes when login button is clicked",
            "Bug #2: NullPointerException in authentication module"
        ]

        response = await provider.generate(
            prompt="What's the likely cause?",
            context=context,
            max_tokens=100,
            temperature=0.1
        )

        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\nContext-aware response: {response}")