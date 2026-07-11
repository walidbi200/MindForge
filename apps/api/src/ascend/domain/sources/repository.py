from typing import Protocol
from uuid import UUID

from ascend.domain.sources.entity import Source, SourceType


class SourceRepository(Protocol):
    def save(self, source: Source) -> None: ...

    def get(self, source_id: UUID) -> Source | None: ...

    def delete(self, source_id: UUID) -> None: ...

    def list(
        self, limit: int = 50, offset: int = 0, source_type: SourceType | None = None, q: str | None = None
    ) -> list[Source]: ...

    def list_by_ids(self, ids: "list[UUID]") -> "list[Source]": ...
