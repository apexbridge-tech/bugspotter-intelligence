from typing import Optional
from psycopg import AsyncConnection

from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm import LLMProvider
from bugspotter_intelligence.db.bug_repository import BugRepository
from bugspotter_intelligence.services.embeddings import EmbeddingProvider


class BugQueryService:
    """
    Handles bug read operations (queries)

    Queries that read state:
    - Get bug details
    - Find similar bugs
    - Get mitigation suggestions
    """

    def __init__(self, settings: Settings, llm_provider: LLMProvider, embedding_provider: EmbeddingProvider):
        self.llm = llm_provider
        self.embeddings = embedding_provider
        self.repo = BugRepository()
        self.settings = settings

    async def get_bug(
            self,
            conn: AsyncConnection,
            bug_id: str
    ) -> Optional[dict]:
        """
        Query: Get bug details by ID

        Returns None if bug not found
        """
        return await self.repo.get_bug(conn, bug_id)

    async def find_similar_bugs(
            self,
            conn: AsyncConnection,
            bug_id: str,
            similarity_threshold: float | None = None,
            limit: int | None = None
    ) -> dict:
        """
        Query: Find bugs similar to the given bug

        Returns:
            {
                "bug_id": str,
                "is_duplicate": bool,
                "similar_bugs": list[dict]
            }
        """
        # Get the bug's embedding
        bug = await self.repo.get_bug(conn, bug_id)

        if not bug:
            raise ValueError(f"Bug {bug_id} not found")

        threshold = similarity_threshold if similarity_threshold is not None else self.settings.similarity_threshold
        max_bugs = limit if limit is not None else self.settings.max_similar_bugs

        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT embedding FROM bug_embeddings WHERE bug_id = %s",
                (bug_id,)
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"Embedding not found for bug {bug_id}")

            embedding = row[0]

        # Find similar bugs
        similar_bugs = await self.repo.find_similar(
            conn=conn,
            embedding=embedding,
            limit=max_bugs + 1,  # +1 because it includes itself
            threshold=threshold
        )

        # Remove the bug itself from results
        similar_bugs = [b for b in similar_bugs if b["bug_id"] != bug_id][:max_bugs]

        # Determine if it's a duplicate
        is_duplicate = False
        if similar_bugs and similar_bugs[0]["similarity"] >= self.settings.duplicate_threshold:
            is_duplicate = True

        return {
            "bug_id": bug_id,
            "is_duplicate": is_duplicate,
            "similar_bugs": similar_bugs,
            "threshold_used": threshold
        }

    async def get_mitigation_suggestion(
            self,
            conn: AsyncConnection,
            bug_id: str,
            use_similar_bugs: bool = True
    ) -> dict:
        """
        Query: Get AI-powered mitigation suggestion for a bug

        Optionally uses similar bugs with resolutions as context
        """
        # Get the bug
        bug = await self.repo.get_bug(conn, bug_id)

        if not bug:
            raise ValueError(f"Bug {bug_id} not found")

        # Get similar bugs if requested
        context = []
        if use_similar_bugs:
            similar_result = await self.find_similar_bugs(conn, bug_id)

            for similar_bug in similar_result["similar_bugs"]:
                if similar_bug.get("resolution"):
                    context.append(
                        f"Similar bug: {similar_bug['title']}\n"
                        f"Resolution: {similar_bug['resolution']}"
                    )

        # Generate mitigation
        suggestion = await self._generate_mitigation(
            title=bug["title"],
            description=bug.get("description"),
            context=context
        )

        return {
            "bug_id": bug_id,
            "mitigation_suggestion": suggestion,
            "based_on_similar_bugs": len(context) > 0
        }

    async def _generate_mitigation(
            self,
            title: str,
            description: Optional[str],
            context: list[str]
    ) -> str:
        """Generate AI mitigation suggestion"""
        prompt_parts = [f"Bug: {title}"]

        if description:
            prompt_parts.append(f"Description: {description}")

        prompt_parts.append(
            "\nProvide a concise, actionable suggestion for how to fix or mitigate this issue."
        )

        prompt = "\n".join(prompt_parts)

        suggestion = await self.llm.generate(
            prompt=prompt,
            context=context if context else None,
            temperature=0.3,
            max_tokens=300
        )

        return suggestion