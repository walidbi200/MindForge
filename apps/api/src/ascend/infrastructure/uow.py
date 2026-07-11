from sqlmodel import Session
from ascend.application.uow import UnitOfWork
from ascend.infrastructure.repositories.capture import SqlAlchemyCaptureRepository

class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session):
        self.session = session
        self.captures = SqlAlchemyCaptureRepository(session)
        
    def commit(self) -> None:
        self.session.commit()
        
    def rollback(self) -> None:
        self.session.rollback()
        
    def __enter__(self) -> 'SqlAlchemyUnitOfWork':
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        self.session.close()
