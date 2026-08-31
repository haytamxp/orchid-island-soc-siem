"""
Data models for the Orchid Island SOC/SIEM AI engine.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class Classification(str, Enum):
    BENIGN = "BENIGN"
    SUSPICIOUS = "SUSPICIOUS"
    SQL_INJECTION = "SQL_INJECTION"
    XSS = "XSS"
    BRUTE_FORCE = "BRUTE_FORCE"
    CSRF = "CSRF"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    MALWARE = "MALWARE"
    CREDENTIAL_ATTACK = "CREDENTIAL_ATTACK"
    SCANNING = "SCANNING"
    COMMAND_EXECUTION = "COMMAND_EXECUTION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityEvent(BaseModel):
    """
    Normalized security event submitted for AI analysis.
    """

    model_config = ConfigDict(
        extra="allow"
    )

    source: str

    description: str = ""
    severity: str | None = None
    rule_id: str | None = None

    src_ip: str | None = None
    dst_ip: str | None = None

    hostname: str | None = None
    username: str | None = None

    url: str | None = None
    http_method: str | None = None
    http_status: int | None = None

    timestamp: str | None = None

    raw_event: dict[str, Any] = Field(
        default_factory=dict
    )


class Evidence(BaseModel):
    """
    Evidence identified by the AI.
    """

    description: str

    category: str = "general"

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


class MITRETechnique(BaseModel):
    """
    MITRE ATT&CK technique identified by the AI.
    """

    technique_id: str

    name: str

    rationale: str


class AIAnalysis(BaseModel):
    """
    Structured analysis returned by Gemini.
    """

    classification: Classification

    severity: Severity

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    summary: str

    evidence: list[Evidence] = Field(
        default_factory=list
    )

    mitre_attack: list[MITRETechnique] = Field(
        default_factory=list
    )

    false_positive_indicators: list[str] = Field(
        default_factory=list
    )

    recommended_actions: list[str] = Field(
        default_factory=list
    )

    playbook: str | None = None

    provider: str = "gemini"

    model: str

    def to_dict(
        self
    ) -> dict[str, Any]:
        """
        Convert the model into JSON-compatible data.
        """

        return self.model_dump(
            mode="json"
        )