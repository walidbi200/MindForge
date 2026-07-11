from typing import Protocol
from ascend.domain.captures.repository import CaptureRepository

class UnitOfWork(Protocol):
    captures: CaptureRepository
    
    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(self) -> 'UnitOfWork':
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...
