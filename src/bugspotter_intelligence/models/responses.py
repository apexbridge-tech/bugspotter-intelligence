from pydantic import BaseModel, Field


class AskResponse(BaseModel):
    """Response model for /ask endpoint"""

    answer: str = Field(
        ...,
        description="AI-generated answer"
    )

    provider: str = Field(
        ...,
        description="LLM provider used (e.g., 'ollama', 'claude')"
    )

    model: str = Field(
        ...,
        description="Model used (e.g., 'llama3.1:8b')"
    )