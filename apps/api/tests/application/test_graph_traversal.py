from datetime import datetime, timezone
from uuid import uuid4

from ascend.application.graph.get_entity_neighborhood import GetEntityNeighborhoodUseCase
from ascend.application.graph.get_relationship_graph import GetRelationshipGraphUseCase
from ascend.application.relationships.create_relationship import CreateRelationshipUseCase
from ascend.domain.captures.entity import Capture
from ascend.domain.relationships.entity import CreatorType, EntityType, RelationshipType
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_graph_traversal(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    # Create graph A -> B -> C -> D and cycle D -> A
    id_a = uuid4()
    id_b = uuid4()
    id_c = uuid4()
    id_d = uuid4()

    with uow:
        uow.captures.save(Capture(id=id_a, content="A", created_at=datetime.now(timezone.utc)))
        uow.captures.save(Capture(id=id_b, content="B", created_at=datetime.now(timezone.utc)))
        uow.captures.save(Capture(id=id_c, content="C", created_at=datetime.now(timezone.utc)))
        uow.captures.save(Capture(id=id_d, content="D", created_at=datetime.now(timezone.utc)))
        uow.commit()

    rel_use_case = CreateRelationshipUseCase(uow)
    rel_use_case.execute(
        uuid4(),
        id_a,
        EntityType.CAPTURE,
        id_b,
        EntityType.CAPTURE,
        RelationshipType.RELATED_TO,
        1.0,
        CreatorType.SYSTEM,
    )
    rel_use_case.execute(
        uuid4(),
        id_b,
        EntityType.CAPTURE,
        id_c,
        EntityType.CAPTURE,
        RelationshipType.RELATED_TO,
        1.0,
        CreatorType.SYSTEM,
    )
    rel_use_case.execute(
        uuid4(),
        id_c,
        EntityType.CAPTURE,
        id_d,
        EntityType.CAPTURE,
        RelationshipType.RELATED_TO,
        1.0,
        CreatorType.SYSTEM,
    )
    rel_use_case.execute(
        uuid4(),
        id_d,
        EntityType.CAPTURE,
        id_a,
        EntityType.CAPTURE,
        RelationshipType.RELATED_TO,
        1.0,
        CreatorType.SYSTEM,
    )

    # 1. Depth 1 (Neighborhood) from A
    neighborhood_use_case = GetEntityNeighborhoodUseCase(uow)
    nodes, edges = neighborhood_use_case.execute(id_a)

    node_ids = {n.id for n in nodes}
    assert id_a in node_ids
    assert id_b in node_ids
    assert id_d in node_ids
    assert id_c not in node_ids
    assert len(nodes) == 3
    assert len(edges) == 2

    # 2. Depth 2 (Path preview) from A
    graph_use_case = GetRelationshipGraphUseCase(uow)
    nodes, edges = graph_use_case.execute(id_a, depth=2)
    node_ids = {n.id for n in nodes}
    assert id_a in node_ids
    assert id_b in node_ids
    assert id_c in node_ids
    assert id_d in node_ids
    assert len(nodes) == 4
    # B->C edge is included because B is depth 1, D->A included because D is depth 1, A->B, D->A
    assert len(edges) == 4

    # 3. Depth limits enforced
    nodes, edges = graph_use_case.execute(id_a, depth=3)  # should cap at 2
    assert len(nodes) == 4
