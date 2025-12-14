from typing import Optional
from psycopg import AsyncConnection
from datetime import datetime


class BugRepository:
    """Data access layer for bug_embeddings table"""

    async def insert_bug(
            self,
            conn: AsyncConnection,
            bug_id: str,
            title: str,
            description: Optional[str],
            embedding: list[float]
    ) -> None:
        """Insert or update bug embedding"""
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO bug_embeddings
                    (bug_id, title, description, embedding, last_accessed)
                VALUES (%s, %s, %s, %s, %s) ON CONFLICT (bug_id) 
                DO
                UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    embedding = EXCLUDED.embedding,
                    updated_at = CURRENT_TIMESTAMP,
                    last_accessed = EXCLUDED.last_accessed
                """,
                (bug_id, title, description, embedding, datetime.now())
            )
            await conn.commit()

    async def find_similar(
            self,
            conn: AsyncConnection,
            embedding: list[float],
            limit: int = 5,
            threshold: float = 0.7
    ) -> list[dict]:
        """
        Find similar bugs using vector similarity

        Returns bugs with similarity score >= threshold
        """
        async with conn.cursor() as cursor:
            # Use cosine similarity
            await cursor.execute(
                """
                SELECT bug_id,
                       title,
                       description,
                       status,
                       resolution,
                       1 - (embedding <=> %s::vector) as similarity
                FROM bug_embeddings
                WHERE 1 - (embedding <=> %s::vector) >= %s
                  AND status != 'duplicate'
                ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """,
                (embedding, embedding, threshold, embedding, limit)
            )

            rows = await cursor.fetchall()

            return [
                {
                    "bug_id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "status": row[3],
                    "resolution": row[4],
                    "similarity": float(row[5])
                }
                for row in rows
            ]