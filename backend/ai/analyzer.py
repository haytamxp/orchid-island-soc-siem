"""
Main Gemini-based SOC analysis orchestrator.
"""

from .errors import (
    AIAnalysisError,
    AIConfigurationError,
    AIResponseValidationError,
    GeminiAPIError,
)
from .gemini import GeminiClient
from .models import (
    AIAnalysis,
    SecurityEvent,
)
from .prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
)
from .validator import validate_analysis


class AIAnalyzer:
    """
    Coordinates the complete SOC AI analysis workflow.
    """

    def __init__(
        self,
        client: GeminiClient,
    ) -> None:

        self.client = client

    def analyze(
        self,
        event: SecurityEvent,
    ) -> AIAnalysis:

        try:

            prompt = build_analysis_prompt(
                event.model_dump(
                    mode="json"
                )
            )

            result = (
                self.client.generate_structured(
                    system_instruction=(
                        SYSTEM_PROMPT
                    ),
                    prompt=prompt,
                    response_model=AIAnalysis,
                )
            )

        except ValueError as exc:

            raise AIConfigurationError(
                str(exc)
            ) from exc

        except RuntimeError as exc:

            raise GeminiAPIError(
                str(exc)
            ) from exc

        if not isinstance(
            result,
            AIAnalysis,
        ):

            raise AIResponseValidationError(
                "Unexpected Gemini response type."
            )

        result = result.model_copy(
            update={
                "provider": "gemini",
                "model": self.client.model,
            }
        )

        try:

            return validate_analysis(
                result
            )

        except AIResponseValidationError:

            raise

        except Exception as exc:

            raise AIAnalysisError(
                f"AI validation failed: {exc}"
            ) from exc