"""
Validation helpers for Gemini AI analysis.
"""

from .errors import AIResponseValidationError
from .models import AIAnalysis


def validate_analysis(
    analysis: AIAnalysis,
) -> AIAnalysis:
    """
    Perform final application-level validation.

    Pydantic already validates the schema. This layer
    exists for business/security rules that are specific
    to the SIEM.
    """

    if not analysis.summary.strip():

        raise AIResponseValidationError(
            "Gemini returned an empty summary."
        )

    if len(
        analysis.recommended_actions
    ) > 10:

        raise AIResponseValidationError(
            "Too many recommended actions."
        )

    if len(
        analysis.evidence
    ) > 20:

        raise AIResponseValidationError(
            "Too many evidence items."
        )

    return analysis