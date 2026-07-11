from ascend.api.v1.endpoints.captures.schemas import CaptureResponse
from ascend.domain.captures.entity import Capture


def to_response(capture: Capture) -> CaptureResponse:
    return CaptureResponse(id=capture.id, content=capture.content, created_at=capture.created_at)
