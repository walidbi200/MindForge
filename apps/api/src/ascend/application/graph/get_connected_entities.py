from uuid import UUID

from ascend.application.graph.get_relationship_graph import Node
from ascend.application.uow import UnitOfWork


class GetConnectedEntitiesUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID) -> list[Node]:
        nodes: dict[UUID, Node] = {}

        with self.uow:
            outgoing = self.uow.relationships.list_outgoing(entity_id)
            incoming = self.uow.relationships.list_incoming(entity_id)

            for rel in outgoing:
                if rel.to_id not in nodes:
                    node = self._fetch_node(rel.to_id)
                    if node:
                        nodes[rel.to_id] = node

            for rel in incoming:
                if rel.from_id not in nodes:
                    node = self._fetch_node(rel.from_id)
                    if node:
                        nodes[rel.from_id] = node

        return list(nodes.values())

    def _fetch_node(self, entity_id: UUID) -> Node | None:
        from ascend.domain.relationships.entity import EntityType

        concept = self.uow.concepts.get(entity_id)
        if concept:
            return Node(id=concept.id, type=EntityType.CONCEPT, title=concept.title)

        source = self.uow.sources.get(entity_id)
        if source:
            return Node(id=source.id, type=EntityType.SOURCE, title=source.title)

        capture = self.uow.captures.get(entity_id)
        if capture:
            title = capture.content[:50] + "..." if len(capture.content) > 50 else capture.content
            return Node(id=capture.id, type=EntityType.CAPTURE, title=title)

        return None
