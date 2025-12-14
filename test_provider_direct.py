import asyncio
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm import create_llm_provider


async def test():
    settings = Settings()
    provider = create_llm_provider(settings)

    print(f"Provider: {type(provider).__name__}")
    print(f"Settings: {settings.ollama_base_url}")

    try:
        response = await provider.generate(
            prompt="Say hello",
            max_tokens=50
        )
        print(f"Success: {response}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


asyncio.run(test())