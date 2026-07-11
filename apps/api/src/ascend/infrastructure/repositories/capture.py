from uuid import UUID

from sqlmodel import Session, select

from ascend.domain.captures.entity import Capture
from ascend.domain.captures.repository import CaptureRepository
from ascend.infrastructure.models.capture import CaptureModel


class SqlAlchemyCaptureRepository(CaptureRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, capture: Capture) -> None:
        model = self.session.get(CaptureModel, capture.id)
        if model:
            model.content = capture.content
            model.status = capture.status.value
        else:
            model = CaptureModel(
                id=capture.id, content=capture.content, status=capture.status.value, created_at=capture.created_at
            )
        self.session.add(model)

    def get(self, capture_id: UUID) -> Capture | None:
        model = self.session.get(CaptureModel, capture_id)
        if not model:
            return None
        from ascend.domain.captures.entity import CaptureStatus

        return Capture(
            id=model.id, content=model.content, status=CaptureStatus(model.status), created_at=model.created_at
        )

    def list(self, limit: int = 50, offset: int = 0, q: str | None = None) -> list[Capture]:
        query = select(CaptureModel)
        if q:
            query = query.where(CaptureModel.content.ilike(f"%{q}%"))

        models = self.session.exec(query.order_by(CaptureModel.created_at.desc()).offset(offset).limit(limit)).all()
        from ascend.domain.captures.entity import CaptureStatus

        return [
            Capture(id=model.id, content=model.content, status=CaptureStatus(model.status), created_at=model.created_at)
            for model in models
        ]

    def delete(self, capture_id: UUID) -> None:
        model = self.session.get(CaptureModel, capture_id)
        if model:
            self.session.delete(model)
