from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.source_events import SourceCreated
from ascend.domain.exceptions import ValidationError
from ascend.domain.sources.entity import Source, SourceType


class CreateSourceUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        source_id: UUID,
        title: str,
        source_type: SourceType,
        uri: str | None = None,
        author: str | None = None,
        publisher: str | None = None,
        language: str | None = None,
        metadata_json: str = "{}",
    ) -> Source:
        if not title or not title.strip():
            raise ValidationError("Title is required.")
        if not source_type:
            raise ValidationError("Source type is required.")

        now = datetime.now(timezone.utc)
        source = Source(
            id=source_id,
            title=title.strip(),
            source_type=source_type,
            uri=uri.strip() if uri else None,
            author=author.strip() if author else None,
            publisher=publisher.strip() if publisher else None,
            language=language.strip() if language else None,
            created_at=now,
            updated_at=now,
            metadata_json=metadata_json,
        )

        with self.uow:
            self.uow.sources.save(source)
            self.uow.emit(SourceCreated(aggregate_id=source.id, title=source.title, source_type=source.source_type))
            self.uow.commit()

        return source
