import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ascend.api.dependencies import get_session
from ascend.api.v1.endpoints.timeline.schemas import TimelineEventResponse
from ascend.infrastructure.repositories.timeline import TimelineRepository

router = APIRouter(prefix="/timeline")


@router.get("", response_model=list[TimelineEventResponse])
def get_timeline(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    aggregate_type: str | None = None,
    event_type: str | None = None,
    session: Session = Depends(get_session),
):
    repo = TimelineRepository(session)
    events = repo.list(limit=limit, offset=offset, aggregate_type=aggregate_type, event_type=event_type)

    responses = []
    for e in events:
        responses.append(
            TimelineEventResponse(
                id=e.id,
                aggregate_id=e.aggregate_id,
                aggregate_type=e.aggregate_type,
                event_type=e.event_type,
                occurred_at=e.occurred_at,
                correlation_id=e.correlation_id,
                version=e.version,
                payload=json.loads(e.payload_json),
            )
        )

    return responses
