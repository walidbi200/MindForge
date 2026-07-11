from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.collections.entity import Collection
from ascend.domain.events.collection_events import CollectionCreated


class CreateCollectionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        collection_id: UUID,
        name: str,
        description: str = "",
        color: str = "#3B82F6",
        icon: str = "book",
        metadata_json: str = "{}",
    ) -> Collection:
        if not name or not name.strip():
            raise ValueError("Collection name is required.")

        name = name.strip()

        with self.uow:
            existing = self.uow.collections.get_by_name(name)
            if existing:
                raise ValueError(f"Collection with name '{name}' already exists.")

            now = datetime.now(timezone.utc)
            collection = Collection(
                id=collection_id,
                name=name,
                description=description,
                color=color,
                icon=icon,
                created_at=now,
                updated_at=now,
                metadata_json=metadata_json,
            )

            self.uow.collections.save(collection)
            self.uow.emit(CollectionCreated(aggregate_id=collection.id, name=collection.name))
            self.uow.commit()

        return collection
