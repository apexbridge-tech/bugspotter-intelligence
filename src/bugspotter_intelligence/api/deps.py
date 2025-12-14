"""FastAPI dependency injection"""

from functools import lru_cache
from fastapi import Depends

from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm import LLMProvider, create_llm_provider


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton)"""
    return Settings()


@lru_cache()
def get_llm_provider() -> LLMProvider:
    """Get cached LLM provider instance (singleton)"""
    settings = get_settings()
    return create_llm_provider(settings)