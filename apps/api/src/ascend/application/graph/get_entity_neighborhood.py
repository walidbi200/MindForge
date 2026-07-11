from uuid import UUID

from ascend.application.graph.get_relationship_graph import GetRelationshipGraphUseCase, Node
from ascend.application.uow import UnitOfWork
from ascend.domain.relationships.entity import Relationship


class GetEntityNeighborhoodUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID) -> tuple[list[Node], list[Relationship]]:
        # Neighborhood is exactly a depth=1 traversal
        traversal = GetRelationshipGraphUseCase(self.uow)
        return traversal.execute(start_id=entity_id, depth=1, max_nodes=100)
