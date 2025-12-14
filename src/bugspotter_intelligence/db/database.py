from typing import AsyncGenerator
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from bugspotter_intelligence.config import Settings


_pool: AsyncConnectionPool | None = None

def create_pool(settings: Settings) -> AsyncConnectionPool:
    """Create async connection pool for PostgreSQL"""

    return AsyncConnectionPool(
        conninfo=settings.database_url,
        min_size=2,
        max_size=10,
    )


async def init_db(settings: Settings) -> None:
    """Initialize database pool"""

    global _pool
    _pool = create_pool(settings)
    await _pool.open()  # Open the pool connections


async def close_db() -> None:
    """Close database pool"""

    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> AsyncConnectionPool:
    """Get the global pool instance"""
    if _pool is None:
        raise ValueError("Database pool not initialized. Call init_db() first.")
    return _pool

async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Get a database connection from the pool"""
    pool = get_pool()
    async with pool.connection() as conn:
        yield conn