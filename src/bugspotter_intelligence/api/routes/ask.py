"""Q&A endpoint using LLM"""

from fastapi import APIRouter, Depends, HTTPException
from bugspotter_intelligence.api.deps import get_llm_provider, get_settings
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm import LLMProvider
from bugspotter_intelligence.models import AskRequest, AskResponse

router = APIRouter(prefix="/ask", tags=["Q&A"])


@router.post("", response_model=AskResponse)
async def ask_question(
        request: AskRequest,
        provider: LLMProvider = Depends(get_llm_provider),
        settings: Settings = Depends(get_settings)
) -> AskResponse:
    """
    Ask a question to the AI

    Similar to:
    - Spring: @PostMapping("/ask")
    - ASP.NET: [HttpPost("ask")]
    """
    try:
        answer = await provider.generate(
            prompt=request.question,
            context=request.context,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return AskResponse(
            answer=answer,
            provider=settings.llm_provider,
            model=getattr(settings, f"{settings.llm_provider}_model")
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {error_details}")  # Print to console
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}\n{error_details}"
        )