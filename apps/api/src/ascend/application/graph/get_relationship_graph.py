from dataclasses import dataclass
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.relationships.entity import EntityType, Relationship


@dataclass(frozen=True)
class Node:
    id: UUID
    type: EntityType
    title: str


class GetRelationshipGraphUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, start_id: UUID, depth: int = 1, max_nodes: int = 100) -> tuple[list[Node], list[Relationship]]:
        if depth > 2:
            depth = 2

        nodes: dict[UUID, Node] = {}
        relationships: dict[UUID, Relationship] = {}

        # We will do a BFS traversal
        # queue stores tuples of (entity_id, current_depth)
        queue: list[tuple[UUID, int]] = [(start_id, 0)]
        visited: set[UUID] = set()

        with self.uow:
            while queue:
                current_id, current_depth = queue.pop(0)

                if current_id in visited:
                    continue
                visited.add(current_id)

                # Fetch node
                node = self._fetch_node(current_id)
                if node:
                    nodes[current_id] = node

                if len(nodes) >= max_nodes:
                    break

                if current_depth < depth:
                    # Fetch edges
                    outgoing = self.uow.relationships.list_outgoing(current_id)
                    incoming = self.uow.relationships.list_incoming(current_id)

                    for rel in outgoing:
                        relationships[rel.id] = rel
                        if rel.to_id not in visited and len(nodes) + len(queue) < max_nodes * 2:
                            queue.append((rel.to_id, current_depth + 1))

                    for rel in incoming:
                        relationships[rel.id] = rel
                        if rel.from_id not in visited and len(nodes) + len(queue) < max_nodes * 2:
                            queue.append((rel.from_id, current_depth + 1))

        return list(nodes.values()), list(relationships.values())

    def _fetch_node(self, entity_id: UUID) -> Node | None:
        # We try Concept first, then Source, then Capture.
        concept = self.uow.concepts.get(entity_id)
        if concept:
            return Node(id=concept.id, type=EntityType.CONCEPT, title=concept.title)

        source = self.uow.sources.get(entity_id)
        if source:
            return Node(id=source.id, type=EntityType.SOURCE, title=source.title)

        capture = self.uow.captures.get(entity_id)
        if capture:
            # Capture doesn't have a title, we'll use a snippet of content
            title = capture.content[:50] + "..." if len(capture.content) > 50 else capture.content
            return Node(id=capture.id, type=EntityType.CAPTURE, title=title)

        return None
