from typing import Generator
from ascend.application.uow import UnitOfWork
from ascend.infrastructure.database import get_session
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork
from fastapi import Depends
from sqlmodel import Session

def get_uow(session: Session = Depends(get_session)) -> Generator[UnitOfWork, None, None]:
    yield SqlAlchemyUnitOfWork(session)
