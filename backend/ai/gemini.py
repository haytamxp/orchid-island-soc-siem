"""
Gemini client for Orchid Island SOC/SIEM.
"""

import os
import time
from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel


T = TypeVar(
    "T",
    bound=BaseModel
)


class GeminiClient:
    """
    Gemini API wrapper with structured-output support.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_retries: int = 2,
        retry_delay: float = 2.0,
    ) -> None:

        self.api_key = (
            api_key
            or os.getenv(
                "GEMINI_API_KEY"
            )
        )

        self.model = (
            model
            or os.getenv(
                "GEMINI_MODEL"
            )
            or "gemini-3.6-flash"
        )

        self.max_retries = max(
            0,
            int(max_retries),
        )

        self.retry_delay = max(
            0.5,
            float(retry_delay),
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def generate_structured(
        self,
        system_instruction: str,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """
        Generate a structured response using a Pydantic schema.
        """

        last_error: Exception | None = None

        for attempt in range(
            self.max_retries + 1
        ):

            try:

                response = (
                    self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                system_instruction
                            ),
                            response_mime_type=(
                                "application/json"
                            ),
                            response_schema=response_model,
                        ),
                    )
                )

                if not response.text:

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return response_model.model_validate_json(
                    response.text
                )

            except Exception as exc:

                last_error = exc

                error_text = str(
                    exc
                ).lower()

                transient = any(
                    indicator in error_text
                    for indicator in (
                        "429",
                        "500",
                        "502",
                        "503",
                        "504",
                        "unavailable",
                        "resource exhausted",
                        "temporarily unavailable",
                    )
                )

                if (
                    not transient
                    or attempt >= self.max_retries
                ):

                    raise RuntimeError(
                        "Gemini structured generation "
                        "failed after "
                        f"{attempt + 1} attempt(s): "
                        f"{exc}"
                    ) from exc

                delay = (
                    self.retry_delay
                    * (2 ** attempt)
                )

                print(
                    "[GEMINI] Temporary provider "
                    f"failure. Retry "
                    f"{attempt + 1}/"
                    f"{self.max_retries} "
                    f"in {delay:.1f}s."
                )

                time.sleep(
                    delay
                )

        raise RuntimeError(
            "Gemini generation failed."
        ) from last_error