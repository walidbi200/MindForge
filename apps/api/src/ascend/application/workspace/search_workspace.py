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
        with self.uow:
            # Captures
            captures = self.uow.captures.list(q=q, limit=limit)
            for c in captures:
                snippet = c.content[:100] + "..." if len(c.content) > 100 else c.content
                results.append(
                    SearchResult(
                        id=c.id,
                        type="Capture",
                        title=snippet[:30],
                        snippet=snippet,
                    )
                )

            # Concepts
            concepts = self.uow.concepts.list(q=q, limit=limit)
            for c in concepts:
                results.append(
                    SearchResult(
                        id=c.id,
                        type="Concept",
                        title=c.title,
                        snippet=c.summary[:100] if c.summary else "",
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
                results.append(
                    SearchResult(
                        id=col.id,
                        type="Collection",
                        title=col.name,
                        snippet=col.description[:100] if col.description else "",
                    )
                )

        return results
