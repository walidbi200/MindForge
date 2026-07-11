from datetime import datetime, timezone
from uuid import uuid4

from ascend.domain.sources.entity import Source, SourceType
from ascend.infrastructure.repositories.source import SqlAlchemySourceRepository


def test_source_repository_crud(db_session):
    repo = SqlAlchemySourceRepository(db_session)
    source_id = uuid4()
    now = datetime.now(timezone.utc)

    source = Source(
        id=source_id,
        title="Test Source",
        source_type=SourceType.WEB_ARTICLE,
        uri="https://example.com/test",
        author="Author Name",
        publisher="Publisher Name",
        language="en",
        created_at=now,
        updated_at=now,
        metadata_json='{"tags": ["test"]}',
    )

    # 1. Save
    repo.save(source)
    db_session.commit()

    # 2. Get
    retrieved = repo.get(source_id)
    assert retrieved is not None
    assert retrieved.title == "Test Source"
    assert retrieved.source_type == SourceType.WEB_ARTICLE
    assert retrieved.uri == "https://example.com/test"
    assert retrieved.author == "Author Name"
    assert retrieved.publisher == "Publisher Name"
    assert retrieved.language == "en"
    assert retrieved.metadata_json == '{"tags": ["test"]}'

    # 3. Update
    retrieved.title = "Updated Source Title"
    repo.save(retrieved)
    db_session.commit()

    updated = repo.get(source_id)
    assert updated.title == "Updated Source Title"

    # 4. List
    sources = repo.list(limit=10, offset=0)
    assert any(s.id == source_id for s in sources)

    sources_filtered = repo.list(limit=10, offset=0, source_type=SourceType.BOOK)
    assert not any(s.id == source_id for s in sources_filtered)

    # 5. Delete
    repo.delete(source_id)
    db_session.commit()
    assert repo.get(source_id) is None
