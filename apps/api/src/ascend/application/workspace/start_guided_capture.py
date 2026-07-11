from typing import Tuple
from uuid import uuid4

from ascend.application.ai.analyze_capture import AnalyzeCaptureUseCase
from ascend.application.ai.protocols import AIResponse, AIService
from ascend.application.captures.create_capture import CreateCaptureUseCase
from ascend.application.uow import UnitOfWork
from ascend.domain.captures.entity import Capture


class StartGuidedCaptureUseCase:
    """
    Orchestrates the creation of a Capture and immediately requests an AI analysis for it.
    Does not mutate any other domain entities until the user explicitly applies the proposal.
    """

    def __init__(self, uow: UnitOfWork, ai_service: AIService):
        self.uow = uow
        self.ai_service = ai_service

    def execute(self, content: str) -> Tuple[Capture, AIResponse]:
        # 1. Create the capture (commits transaction 1)
        capture_id = uuid4()
        create_use_case = CreateCaptureUseCase(self.uow)
        capture = create_use_case.execute(capture_id=capture_id, content=content)

        # 2. Analyze the capture (commits transaction 2 with timeline events)
        analyze_use_case = AnalyzeCaptureUseCase(self.uow, self.ai_service)
        ai_response = analyze_use_case.execute(capture_id=capture.id)

        return capture, ai_response
