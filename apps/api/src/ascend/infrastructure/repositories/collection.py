from uuid import UUID

from sqlmodel import Session, select

from ascend.domain.collections.entity import Collection, Membership
from ascend.domain.collections.repository import CollectionRepository, MembershipRepository
from ascend.infrastructure.models.collection import CollectionModel, MembershipModel


class SqlAlchemyCollectionRepository(CollectionRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, collection: Collection) -> None:
        model = self.session.get(CollectionModel, collection.id)
        if model:
            model.name = collection.name
            model.description = collection.description
            model.color = collection.color
            model.icon = collection.icon
            model.updated_at = collection.updated_at
            model.metadata_json = collection.metadata_json
        else:
            model = CollectionModel(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                color=collection.color,
                icon=collection.icon,
                created_at=collection.created_at,
                updated_at=collection.updated_at,
                metadata_json=collection.metadata_json,
            )
        self.session.add(model)

    def get(self, collection_id: UUID) -> Collection | None:
        model = self.session.get(CollectionModel, collection_id)
        if not model:
            return None
        return self._to_entity(model)

    def get_by_name(self, name: str) -> Collection | None:
        model = self.session.exec(select(CollectionModel).where(CollectionModel.name == name)).first()
        if not model:
            return None
        return self._to_entity(model)

    def delete(self, collection_id: UUID) -> None:
        model = self.session.get(CollectionModel, collection_id)
        if model:
            self.session.delete(model)

    def list(
        self,
        q: str | None = None,
        color: str | None = None,
        icon: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Collection]:
        statement = select(CollectionModel)
        if q:
            statement = statement.where(
                (CollectionModel.name.like(f"%{q}%")) | (CollectionModel.description.like(f"%{q}%"))
            )
        if color:
            statement = statement.where(CollectionModel.color == color)
        if icon:
            statement = statement.where(CollectionModel.icon == icon)

        statement = statement.order_by(CollectionModel.created_at.desc()).offset(offset).limit(limit)
        models = self.session.exec(statement).all()
        return [self._to_entity(model) for model in models]

    def list_by_ids(self, ids: "list[UUID]") -> "list[Collection]":
        if not ids:
            return []
        statement = select(CollectionModel).where(CollectionModel.id.in_(ids))
        models = self.session.exec(statement).all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: CollectionModel) -> Collection:
        return Collection(
            id=model.id,
            name=model.name,
            description=model.description,
            color=model.color,
            icon=model.icon,
            created_at=model.created_at,
            updated_at=model.updated_at,
            metadata_json=model.metadata_json,
        )


class SqlAlchemyMembershipRepository(MembershipRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, membership: Membership) -> None:
        model = MembershipModel(
            id=membership.id,
            collection_id=membership.collection_id,
            entity_id=membership.entity_id,
            entity_type=membership.entity_type,
            created_at=membership.created_at,
            position=membership.position,
        )
        self.session.merge(model)

    def get(self, membership_id: UUID) -> Membership | None:
        model = self.session.get(MembershipModel, membership_id)
        if not model:
            return None
        return self._to_entity(model)

    def delete(self, membership_id: UUID) -> None:
        model = self.session.get(MembershipModel, membership_id)
        if model:
            self.session.delete(model)

    def find(self, collection_id: UUID, entity_id: UUID) -> Membership | None:
        model = self.session.exec(
            select(MembershipModel)
            .where(MembershipModel.collection_id == collection_id)
            .where(MembershipModel.entity_id == entity_id)
        ).first()
        if not model:
            return None
        return self._to_entity(model)

    def list_by_collection(self, collection_id: UUID) -> list[Membership]:
        models = self.session.exec(
            select(MembershipModel)
            .where(MembershipModel.collection_id == collection_id)
            .order_by(MembershipModel.position.asc(), MembershipModel.created_at.asc())
        ).all()
        return [self._to_entity(model) for model in models]

    def list_by_entity(self, entity_id: UUID) -> list[Membership]:
        models = self.session.exec(
            select(MembershipModel)
            .where(MembershipModel.entity_id == entity_id)
            .order_by(MembershipModel.position.asc(), MembershipModel.created_at.asc())
        ).all()
        return [self._to_entity(model) for model in models]

    def delete_by_collection(self, collection_id: UUID) -> None:
        models = self.session.exec(select(MembershipModel).where(MembershipModel.collection_id == collection_id)).all()
        for m in models:
            self.session.delete(m)

    def delete_by_entity(self, entity_id: UUID) -> None:
        models = self.session.exec(select(MembershipModel).where(MembershipModel.entity_id == entity_id)).all()
        for m in models:
            self.session.delete(m)

    def _to_entity(self, model: MembershipModel) -> Membership:
        return Membership(
            id=model.id,
            collection_id=model.collection_id,
            entity_id=model.entity_id,
            entity_type=model.entity_type,
            created_at=model.created_at,
            position=model.position,
        )
