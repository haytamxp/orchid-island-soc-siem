"""
Exceptions used by the AI analysis engine.
"""


class AIError(Exception):
    """
    Base exception for AI engine errors.
    """


class AIConfigurationError(AIError):
    """
    AI configuration is missing or invalid.
    """


class GeminiAPIError(AIError):
    """
    Gemini API communication failure.
    """


class AIResponseValidationError(AIError):
    """
    Gemini returned invalid or unsafe analysis data.
    """


class AIAnalysisError(AIError):
    """
    General AI analysis failure.
    """