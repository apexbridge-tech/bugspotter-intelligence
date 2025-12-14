"""Database migrations and schema setup"""

from psycopg import AsyncConnection


async def create_tables(conn: AsyncConnection) -> None:
    """
    Create all required tables

    Called during application startup to ensure schema exists
    """
    async with conn.cursor() as cursor:
        # Enable pgvector extension
        await cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create bug_embeddings table
        await cursor.execute("""
                             CREATE TABLE IF NOT EXISTS bug_embeddings
                             (
                                 bug_id
                                 TEXT
                                 PRIMARY
                                 KEY,
                                 title
                                 TEXT
                                 NOT
                                 NULL,
                                 description
                                 TEXT,
                                 status
                                 TEXT
                                 DEFAULT
                                 'open',
                                 resolution
                                 TEXT,
                                 resolution_summary
                                 TEXT,
                                 embedding
                                 VECTOR
                             (
                                 384
                             ),
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 last_accessed TIMESTAMP
                                 );
                             """)

        # Create indexes
        await cursor.execute("""
                             CREATE INDEX IF NOT EXISTS bug_embeddings_embedding_idx
                                 ON bug_embeddings
                                 USING ivfflat (embedding vector_cosine_ops)
                                 WITH (lists = 100);
                             """)

        await cursor.execute("""
                             CREATE INDEX IF NOT EXISTS bug_embeddings_status_idx
                                 ON bug_embeddings(status);
                             """)

        await cursor.execute("""
                             CREATE INDEX IF NOT EXISTS bug_embeddings_accessed_idx
                                 ON bug_embeddings(last_accessed);
                             """)

        await conn.commit()
        print("✅ Database tables created successfully")