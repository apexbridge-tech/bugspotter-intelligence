from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.api.routes.ask import router as ask_router

API_PREFIX = "/api/v1"

def register_routes(app: FastAPI) -> None:
    app.include_router(ask_router, prefix=API_PREFIX)


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title="BugSpotter Intelligence API",
                  description="Store bugs in the knowledge base and filter out the duplicates",
                  version="0.1.0",
                  docs_url="/docs",
                  redoc_url="/redoc")  # What parameters should FastAPI() take?

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Which domains can call your API
        allow_credentials=True,  # Allow cookies
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # Allow all headers
    )

    register_routes(app)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "bugspotter_intelligence.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
