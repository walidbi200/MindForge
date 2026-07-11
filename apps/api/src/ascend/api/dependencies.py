from typing import Generator

from fastapi import Depends
from sqlmodel import Session

from ascend.application.uow import UnitOfWork
from ascend.infrastructure.database import get_session
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def get_uow(session: Session = Depends(get_session)) -> Generator[UnitOfWork, None, None]:
    bus = EventBus()
    yield SqlAlchemyUnitOfWork(session, bus)
