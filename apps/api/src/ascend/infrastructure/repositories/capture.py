from uuid import UUID
from sqlmodel import Session, select
from ascend.domain.captures.entity import Capture
from ascend.domain.captures.repository import CaptureRepository
from ascend.infrastructure.models.capture import CaptureModel

class SqlAlchemyCaptureRepository(CaptureRepository):
    def __init__(self, session: Session):
        self.session = session
        
    def save(self, capture: Capture) -> None:
        model = CaptureModel(
            id=capture.id,
            content=capture.content,
            created_at=capture.created_at
        )
        self.session.add(model)
        
    def get(self, capture_id: UUID) -> Capture | None:
        model = self.session.get(CaptureModel, capture_id)
        if not model:
            return None
        return Capture(
            id=model.id,
            content=model.content,
            created_at=model.created_at
        )
        
    def list(self) -> list[Capture]:
        models = self.session.exec(select(CaptureModel)).all()
        return [
            Capture(
                id=model.id,
                content=model.content,
                created_at=model.created_at
            ) for model in models
        ]
        
    def delete(self, capture_id: UUID) -> None:
        model = self.session.get(CaptureModel, capture_id)
        if model:
            self.session.delete(model)
