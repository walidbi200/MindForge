from dataclasses import dataclass
from uuid import UUID

from ascend.application.uow import UnitOfWork


@dataclass(frozen=True)
class SearchResult:
    id: UUID
    type: str
    title: str
    snippet: str


class SearchWorkspaceUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, q: str, limit: int = 20) -> list[SearchResult]:
        if not q or not q.strip():
            return []

        results: list[SearchResult] = []
        q_lower = q.lower()

        def make_snippet(text: str, query: str) -> str:
            if not text:
                return ""
            idx = text.lower().find(query)
            if idx == -1:
                return text[:100] + "..." if len(text) > 100 else text
            start = max(0, idx - 40)
            end = min(len(text), idx + len(query) + 40)
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            return snippet

        with self.uow:
            # Captures
            captures = self.uow.captures.list(q=q, limit=limit)
            for c in captures:
                snippet = make_snippet(c.content, q_lower)
                results.append(
                    SearchResult(
                        id=c.id,
                        type="Capture",
                        title=c.content[:30] + "...",
                        snippet=snippet,
                    )
                )

            # Concepts
            concepts = self.uow.concepts.list(q=q, limit=limit)
            for c in concepts:
                snippet = make_snippet(c.summary or "", q_lower)
                if not snippet and q_lower in c.title.lower():
                    snippet = "Matches title."
                results.append(
                    SearchResult(
                        id=c.id,
                        type="Concept",
                        title=c.title,
                        snippet=snippet,
                    )
                )

            # Sources
            sources = self.uow.sources.list(q=q, limit=limit)
            for s in sources:
                results.append(
                    SearchResult(
                        id=s.id,
                        type="Source",
                        title=s.title,
                        snippet=str(s.uri) if s.uri else "",
                    )
                )

            # Collections
            collections = self.uow.collections.list(q=q, limit=limit)
            for col in collections:
                snippet = make_snippet(col.description or "", q_lower)
                if not snippet and q_lower in col.name.lower():
                    snippet = "Matches title."
                results.append(
                    SearchResult(
                        id=col.id,
                        type="Collection",
                        title=col.name,
                        snippet=snippet,
                    )
                )

        return results
