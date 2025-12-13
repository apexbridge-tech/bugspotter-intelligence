import os
import httpx
from typing import Optional
from .base import LLMProvider
from .factory import register_provider

@register_provider("ollama")
class OllamaProvider(LLMProvider):
    """LLM provider using local Ollama"""
    def __init__(self, settings):
        super().__init__(settings)
        self.API_TIMEOUT = float(os.getenv('OLLAMA_TIMEOUT', '120'))

    async def generate(
            self,
            prompt: str,
            context: Optional[list[str]] = None,
            temperature: float = 0.7,
            max_tokens: int = 1000
    ) -> str:
        """Generate a response from the Ollama LLM"""
        full_prompt = self._build_context_prompt(prompt, context)

        payload = {
            "model": self.settings.ollama_model,
            "prompt": full_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
            response = await client.post(
                f"{self.settings.ollama_base_url}/api/generate",
                json=payload,
            )

            try:
                response.raise_for_status()
                result = response.json()
                return result["response"]
            except httpx.HTTPStatusError as e:
                raise Exception(f"Ollama API error: {e.response.status_code} - {e.response.text}")
            except KeyError:
                raise Exception(f"Unexpected Ollama response format: {response.text}")