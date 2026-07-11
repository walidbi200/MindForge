from uuid import UUID

from sqlmodel import Session, select

from ascend.domain.sources.entity import Source, SourceType
from ascend.domain.sources.repository import SourceRepository
from ascend.infrastructure.models.source import SourceModel


class SqlAlchemySourceRepository(SourceRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, source: Source) -> None:
        # Check if model already exists for update
        model = self.session.get(SourceModel, source.id)
        if model:
            model.title = source.title
            model.source_type = source.source_type
            model.uri = source.uri
            model.author = source.author
            model.publisher = source.publisher
            model.language = source.language
            model.updated_at = source.updated_at
            model.metadata_json = source.metadata_json
        else:
            model = SourceModel(
                id=source.id,
                title=source.title,
                source_type=source.source_type,
                uri=source.uri,
                author=source.author,
                publisher=source.publisher,
                language=source.language,
                created_at=source.created_at,
                updated_at=source.updated_at,
                metadata_json=source.metadata_json,
            )
        self.session.add(model)

    def get(self, source_id: UUID) -> Source | None:
        model = self.session.get(SourceModel, source_id)
        if not model:
            return None
        return self._to_entity(model)

    def delete(self, source_id: UUID) -> None:
        model = self.session.get(SourceModel, source_id)
        if model:
            self.session.delete(model)

    def list(self, limit: int = 50, offset: int = 0, source_type: SourceType | None = None) -> list[Source]:
        statement = select(SourceModel)
        if source_type:
            statement = statement.where(SourceModel.source_type == source_type)
        statement = statement.offset(offset).limit(limit)
        models = self.session.exec(statement).all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: SourceModel) -> Source:
        return Source(
            id=model.id,
            title=model.title,
            source_type=model.source_type,
            uri=model.uri,
            author=model.author,
            publisher=model.publisher,
            language=model.language,
            created_at=model.created_at,
            updated_at=model.updated_at,
            metadata_json=model.metadata_json,
        )
