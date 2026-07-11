from collections.abc import Generator
from sqlmodel import create_engine, Session
from ascend.core.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
