from uuid import UUID

from ascend.application.graph.get_relationship_graph import Node
from ascend.application.uow import UnitOfWork
from ascend.domain.relationships.entity import EntityType


class ListCollectionEntitiesUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, collection_id: UUID) -> list[Node]:
        nodes: list[Node] = []
        with self.uow:
            memberships = self.uow.memberships.list_by_collection(collection_id)
            for m in memberships:
                node = self._fetch_node(m.entity_id, m.entity_type)
                if node:
                    nodes.append(node)
        return nodes

    def _fetch_node(self, entity_id: UUID, entity_type: EntityType) -> Node | None:
        if entity_type == EntityType.CONCEPT:
            concept = self.uow.concepts.get(entity_id)
            if concept:
                return Node(id=concept.id, type=EntityType.CONCEPT, title=concept.title)
        elif entity_type == EntityType.SOURCE:
            source = self.uow.sources.get(entity_id)
            if source:
                return Node(id=source.id, type=EntityType.SOURCE, title=source.title)
        elif entity_type == EntityType.CAPTURE:
            capture = self.uow.captures.get(entity_id)
            if capture:
                title = capture.content[:50] + "..." if len(capture.content) > 50 else capture.content
                return Node(id=capture.id, type=EntityType.CAPTURE, title=title)
        return None
