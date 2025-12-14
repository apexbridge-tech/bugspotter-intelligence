from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    """Request model for /ask endpoint"""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The question to ask the AI",
        examples=["What causes null pointer exceptions?"]
    )

    context: list[str] | None = Field(
        default=None,
        description="Optional context strings (e.g., similar bug descriptions)",
        examples=[["Bug #1: App crashes on login", "Bug #2: Null pointer in auth"]]
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Randomness of response (0.0 = deterministic, 1.0 = creative)"
    )

    max_tokens: int = Field(
        default=500,
        ge=10,
        le=2000,
        description="Maximum length of response"
    )