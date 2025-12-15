import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.db.migrations import create_tables
from bugspotter_intelligence.db.database import init_db, close_db
from bugspotter_intelligence.api.routes import ask, bugs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

API_PREFIX = "/api/v1"

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    settings = Settings()

    try:
        await init_db(settings)
        logger.info("Database pool initialized")

        # Run migrations
        from bugspotter_intelligence.db.database import get_pool
        pool = get_pool()
        async with pool.connection() as conn:
            await create_tables(conn)

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise  # Re-raise to prevent app from starting

    yield  # App runs here

    # Shutdown
    try:
        await close_db()
        logger.info("Database pool closed")
    except Exception as e:
        logger.warning(f"Error closing database: {e}")
        # Don't re-raise on shutdown - just log it


def register_routes(app: FastAPI) -> None:
    app.include_router(ask.router, prefix=API_PREFIX)
    app.include_router(bugs.router, prefix=API_PREFIX)


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title="BugSpotter Intelligence API",
                  description="Store bugs in the knowledge base and filter out the duplicates",
                  version="0.1.0",
                  docs_url="/docs",
                  redoc_url="/redoc",
                  lifespan=lifespan)  # What parameters should FastAPI() take?

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
