from typing import Optional
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


class SimilarBug(BaseModel):
    """Model for a similar bug in search results"""

    bug_id: str
    title: str
    description: Optional[str] = None
    status: str
    resolution: Optional[str] = None
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")


class AnalyzeBugResponse(BaseModel):
    """Response model for bug analysis"""

    bug_id: str
    embedding_generated: bool
    stored: bool = True


class SimilarBugsResponse(BaseModel):
    """Response model for similar bugs query"""

    bug_id: str
    is_duplicate: bool
    similar_bugs: list[SimilarBug]
    threshold_used: float


class MitigationResponse(BaseModel):
    """Response model for mitigation suggestion"""

    bug_id: str
    mitigation_suggestion: str
    based_on_similar_bugs: bool


class BugDetailResponse(BaseModel):
    """Response model for bug details"""

    bug_id: str
    title: str
    description: Optional[str] = None
    status: str
    resolution: Optional[str] = None
    resolution_summary: Optional[str] = None
    created_at: str
    updated_at: str


class ResolutionUpdateResponse(BaseModel):
    """Response model for resolution update"""

    bug_id: str
    status: str
    resolution_summary: str
    updated: bool = True