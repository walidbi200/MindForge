from uuid import UUID

from ascend.application.uow import UnitOfWork


def cleanup_entity_memberships(uow: UnitOfWork, entity_id: UUID) -> None:
    uow.memberships.delete_by_entity(entity_id)
