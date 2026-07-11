from pathlib import Path
from uuid import UUID

from ascend.application.ai.protocols import AIRequest, AIResponse, AIService
from ascend.application.uow import UnitOfWork
from ascend.domain.events.ai_events import AIAnalysisCompleted, AIAnalysisFailed, AIAnalysisRequested
from ascend.domain.exceptions import EntityNotFoundError


class AnalyzeCaptureUseCase:
    def __init__(self, uow: UnitOfWork, ai_service: AIService):
        self.uow = uow
        self.ai_service = ai_service

    def execute(self, capture_id: UUID) -> AIResponse:
        with self.uow:
            capture = self.uow.captures.get(capture_id)
            if not capture:
                raise EntityNotFoundError(f"Capture {capture_id} does not exist.")

            # Load prompts
            prompts_dir = Path(__file__).parent.parent.parent / "infrastructure" / "ai" / "prompts"
            with open(prompts_dir / "system.md", "r") as f:
                system_prompt = f.read()

            with open(prompts_dir / "analyze_capture.md", "r") as f:
                analyze_prompt_template = f.read()

            user_prompt = analyze_prompt_template.replace("{capture_content}", capture.content).replace(
                "{source_context}", ""
            )

            request = AIRequest(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=2000,
            )

            # Log request event
            self.uow.emit(
                AIAnalysisRequested(
                    aggregate_id=capture_id,
                    provider="openrouter",
                    model="configured-model",  # OpenRouter config handles exact model
                    metadata={"action": "analyze_capture"},
                )
            )

            # Call AI
            try:
                response = self.ai_service.generate(request)
            except Exception as e:
                self.uow.emit(
                    AIAnalysisFailed(
                        aggregate_id=capture_id,
                        provider="openrouter",
                        model="configured-model",
                        error_message=str(e),
                        metadata={"action": "analyze_capture"},
                    )
                )
                self.uow.commit()  # Commit the failure event to timeline
                raise e

            # Log success event
            self.uow.emit(
                AIAnalysisCompleted(
                    aggregate_id=capture_id,
                    provider=response.metadata.get("provider", "unknown"),
                    model=response.metadata.get("model", "unknown"),
                    prompt_tokens=response.metadata.get("prompt_tokens", 0),
                    completion_tokens=response.metadata.get("completion_tokens", 0),
                    latency_ms=response.metadata.get("latency_ms", 0),
                    metadata={"action": "analyze_capture", "proposal": response.model_dump()},
                )
            )

            # Commit events (Timeline logging)
            self.uow.commit()

            return response
