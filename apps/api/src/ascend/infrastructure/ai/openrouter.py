import json
import logging
import time

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ascend.application.ai.protocols import AIRequest, AIResponse, AIService
from ascend.core.settings import settings

logger = logging.getLogger(__name__)


class OpenRouterAPIError(Exception):
    """Exception raised when OpenRouter returns a non-200 status code or malformed response."""
    pass


class OpenRouterAIService(AIService):
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "MindForge",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException, OpenRouterAPIError)),
        reraise=True,
    )
    def generate(self, request: AIRequest) -> AIResponse:
        start_time = time.time()
        
        # We enforce structured JSON format response for all models using standard prompts and OpenRouter json object
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise OpenRouterAPIError(f"OpenRouter API returned {response.status_code}")

            data = response.json()
            
            # Extract basic telemetry
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            latency_ms = int((time.time() - start_time) * 1000)

            # Extract content
            message_content = data["choices"][0]["message"]["content"]
            
            logger.info(
                f"OpenRouter call successful: {self.model} "
                f"| {latency_ms}ms | {prompt_tokens} prompt tokens | {completion_tokens} completion tokens"
            )

            # Parse the JSON string from the model into our Pydantic schema
            json_response = json.loads(message_content)
            return AIResponse(
                **json_response,
                metadata={
                    "provider": "openrouter",
                    "model": self.model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "latency_ms": latency_ms,
                }
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse or validate AI response: {str(e)} | Raw output: {message_content}")
            raise OpenRouterAPIError("Invalid response structure from AI provider") from e
