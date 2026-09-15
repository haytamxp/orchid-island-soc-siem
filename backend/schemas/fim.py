"""
Validation schemas for File Integrity Monitoring.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FIMBaselineRequest(BaseModel):
    """
    Register a trusted baseline.

    The snapshot fields are supplied by the monitoring agent, not inferred
    from the Flask server's local filesystem.
    """

    model_config = ConfigDict(extra="forbid")

    hostname: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=4096)

    sha256: str = Field(
        min_length=64,
        max_length=64,
    )

    file_size: int = Field(
        ge=0,
    )

    mode: str | None = Field(
        default=None,
        max_length=32,
    )

    owner_name: str | None = Field(
        default=None,
        max_length=255,
    )

    agent_id: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, value: str) -> str:
        normalized = value.lower()

        if any(character not in "0123456789abcdef" for character in normalized):
            raise ValueError("sha256 must contain hexadecimal characters only")

        return normalized


class FIMEventRequest(BaseModel):
    """Payload submitted by a monitoring agent."""

    model_config = ConfigDict(extra="forbid")

    hostname: str = Field(
        min_length=1,
        max_length=255,
    )

    file_path: str = Field(
        min_length=1,
        max_length=4096,
    )

    change_type: str = Field(
        min_length=1,
        max_length=32,
    )

    old_hash: str | None = Field(
        default=None,
        max_length=64,
    )

    new_hash: str | None = Field(
        default=None,
        max_length=64,
    )

    old_size: int | None = Field(
        default=None,
        ge=0,
    )

    new_size: int | None = Field(
        default=None,
        ge=0,
    )

    severity: str = Field(
        min_length=1,
        max_length=32,
    )

    actor: str | None = Field(
        default=None,
        max_length=255,
    )

    process_name: str | None = Field(
        default=None,
        max_length=255,
    )

    agent_id: str | None = Field(
        default=None,
        max_length=255,
    )

    details: str | None = Field(
        default=None,
        max_length=10000,
    )

    @field_validator("change_type")
    @classmethod
    def validate_change_type(cls, value: str) -> str:
        normalized = value.lower()

        allowed = {
            "added",
            "modified",
            "deleted",
        }

        if normalized not in allowed:
            raise ValueError(
                f"change_type must be one of: {', '.join(sorted(allowed))}"
            )

        return normalized

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        normalized = value.capitalize()

        allowed = {
            "Low",
            "Medium",
            "High",
            "Critical",
        }

        if normalized not in allowed:
            raise ValueError(
                f"severity must be one of: {', '.join(sorted(allowed))}"
            )

        return normalized


class FIMCheckRequest(BaseModel):
    """Payload for an optional backend-side integrity check."""

    model_config = ConfigDict(extra="forbid")

    hostname: str = Field(
        min_length=1,
        max_length=255,
    )

    file_path: str = Field(
        min_length=1,
        max_length=4096,
    )