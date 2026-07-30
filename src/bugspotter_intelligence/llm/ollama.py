import os
import httpx
from typing import Optional
from .base import LLMProvider, Usage
from .exceptions import LLMBackendUnavailableError
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
        text, _ = await self.generate_with_usage(prompt, context, temperature, max_tokens)
        return text

    async def generate_with_usage(
            self,
            prompt: str,
            context: Optional[list[str]] = None,
            temperature: float = 0.7,
            max_tokens: int = 1000,
    ) -> tuple[str, Usage]:
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

        timeout = httpx.Timeout(self.API_TIMEOUT, read=self.API_TIMEOUT)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.settings.ollama_base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                text = result["response"]
        except httpx.RequestError as e:
            # Transport-level failure - connection refused, timeout, DNS, etc.
            # Ollama is unreachable: a down dependency, not an internal error.
            # Surfaced as HTTP 503 at the API boundary.
            raise LLMBackendUnavailableError(
                f"Ollama backend unavailable at {self.settings.ollama_base_url}: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            # 5xx from Ollama means the backend is down/overloaded -> 503.
            # Other statuses (e.g. 4xx) are genuine request errors.
            if e.response.status_code >= 500:
                raise LLMBackendUnavailableError(
                    f"Ollama backend error {e.response.status_code} "
                    f"at {self.settings.ollama_base_url}"
                ) from e
            raise RuntimeError(
                f"Ollama API error: {e.response.status_code} - {e.response.text}"
            ) from e
        except (ValueError, KeyError, TypeError) as e:
            # ValueError covers JSONDecodeError (malformed body); KeyError
            # covers a dict without "response"; TypeError covers a JSON
            # body that decoded to a non-dict (list / primitive) where
            # subscript access fails.
            raise RuntimeError(
                f"Unexpected Ollama response format: {response.text}"
            ) from e

        usage = Usage(
            input=result.get("prompt_eval_count"),
            output=result.get("eval_count"),
            extra={
                k: result[k]
                for k in (
                    "eval_duration",
                    "prompt_eval_duration",
                    "total_duration",
                    "load_duration",
                )
                if k in result
            },
        )
        return text, usage