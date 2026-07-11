from typing import Protocol

class UnitOfWork(Protocol):
    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(self) -> 'UnitOfWork':
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...
