from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.collections.entity import Collection
from ascend.domain.events.collection_events import CollectionUpdated


class UpdateCollectionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        collection_id: UUID,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
        icon: str | None = None,
        metadata_json: str | None = None,
    ) -> Collection | None:
        with self.uow:
            collection = self.uow.collections.get(collection_id)
            if not collection:
                return None

            if name is not None:
                name = name.strip()
                if not name:
                    raise ValueError("Collection name cannot be empty.")
                if name != collection.name:
                    existing = self.uow.collections.get_by_name(name)
                    if existing:
                        raise ValueError(f"Collection with name '{name}' already exists.")
                collection.name = name

            if description is not None:
                collection.description = description

            if color is not None:
                collection.color = color

            if icon is not None:
                collection.icon = icon

            if metadata_json is not None:
                collection.metadata_json = metadata_json

            collection.updated_at = datetime.now(timezone.utc)

            self.uow.collections.save(collection)
            self.uow.emit(CollectionUpdated(aggregate_id=collection.id, name=collection.name))
            self.uow.commit()

        return collection
