from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "bugspotter_intelligence"
    database_user: str = "postgres"
    database_password: str = "postgres"

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: float = 120.0
    anthropic_api_key: str | None = None
    claude_model: str = "claude-sonnet-4-20250514"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4"
    log_level: str = "INFO"
    debug: bool = False
    embedding_provider: str = "local"  # local, openai
    embedding_model: str | None = None  # Provider-specific model name

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False  # DATABASE_URL = database_url
    )

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
