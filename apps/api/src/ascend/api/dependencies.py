from typing import Generator

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from ascend.application.uow import UnitOfWork
from ascend.core.settings import settings
from ascend.infrastructure.database import get_session
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def get_uow(session: Session = Depends(get_session)) -> Generator[UnitOfWork, None, None]:
    bus = EventBus()
    yield SqlAlchemyUnitOfWork(session, bus)


def verify_app_key(x_ascend_key: str = Header(default="")) -> None:
    """Reject requests that don't carry the shared app secret.

    When APP_SECRET_KEY is empty (local dev with no env var) the guard is bypassed
    so there is no friction during development.
    """
    if settings.APP_SECRET_KEY and x_ascend_key != settings.APP_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

