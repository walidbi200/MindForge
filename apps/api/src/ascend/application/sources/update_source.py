from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.source_events import SourceUpdated
from ascend.domain.exceptions import ValidationError
from ascend.domain.sources.entity import Source, SourceType


class UpdateSourceUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        source_id: UUID,
        title: str | None = None,
        source_type: SourceType | None = None,
        uri: str | None = None,
        author: str | None = None,
        publisher: str | None = None,
        language: str | None = None,
        metadata_json: str | None = None,
    ) -> Source | None:
        with self.uow:
            source = self.uow.sources.get(source_id)
            if not source:
                return None

            if title is not None:
                if not title.strip():
                    raise ValidationError("Title cannot be empty.")
                source.title = title.strip()

            if source_type is not None:
                source.source_type = source_type

            if uri is not None:
                source.uri = uri.strip() if uri else None

            if author is not None:
                source.author = author.strip() if author else None

            if publisher is not None:
                source.publisher = publisher.strip() if publisher else None

            if language is not None:
                source.language = language.strip() if language else None

            if metadata_json is not None:
                source.metadata_json = metadata_json

            source.updated_at = datetime.now(timezone.utc)

            self.uow.sources.save(source)
            self.uow.emit(SourceUpdated(aggregate_id=source.id, title=source.title, source_type=source.source_type))
            self.uow.commit()

        return source
