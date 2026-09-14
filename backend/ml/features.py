"""
Feature extraction for the Orchid Island ML risk engine.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SecurityEventFeatures:
    severity: float
    source_is_suricata: float
    source_is_wazuh: float
    source_is_cloudflare: float
    source_is_web: float
    has_source_ip: float
    has_destination_ip: float
    has_username: float
    has_hostname: float
    http_request: float
    http_error: float
    authentication_event: float
    failed_authentication: float
    suspicious_category: float
    brute_force: float
    scanning: float
    sql_injection: float
    xss: float
    path_traversal: float
    command_execution: float
    malware: float
    credential_attack: float
    data_exfiltration: float
    unusual_port: float
    high_risk_port: float

    def to_vector(self) -> list[float]:
        return [
            self.severity,
            self.source_is_suricata,
            self.source_is_wazuh,
            self.source_is_cloudflare,
            self.source_is_web,
            self.has_source_ip,
            self.has_destination_ip,
            self.has_username,
            self.has_hostname,
            self.http_request,
            self.http_error,
            self.authentication_event,
            self.failed_authentication,
            self.suspicious_category,
            self.brute_force,
            self.scanning,
            self.sql_injection,
            self.xss,
            self.path_traversal,
            self.command_execution,
            self.malware,
            self.credential_attack,
            self.data_exfiltration,
            self.unusual_port,
            self.high_risk_port,
        ]


FEATURE_NAMES = [
    "severity",
    "source_is_suricata",
    "source_is_wazuh",
    "source_is_cloudflare",
    "source_is_web",
    "has_source_ip",
    "has_destination_ip",
    "has_username",
    "has_hostname",
    "http_request",
    "http_error",
    "authentication_event",
    "failed_authentication",
    "suspicious_category",
    "brute_force",
    "scanning",
    "sql_injection",
    "xss",
    "path_traversal",
    "command_execution",
    "malware",
    "credential_attack",
    "data_exfiltration",
    "unusual_port",
    "high_risk_port",
]


SEVERITY_MAP = {
    "low": 0.20,
    "medium": 0.45,
    "high": 0.75,
    "critical": 1.00,
}


SUSPICIOUS_CATEGORIES = {
    "attack",
    "intrusion",
    "exploit",
    "malware",
    "credential_attack",
    "scanning",
    "web_attack",
    "authentication_attack",
}


HIGH_RISK_PORTS = {
    22,
    23,
    445,
    3389,
    5985,
    5986,
    1433,
    3306,
    5432,
    6379,
    9200,
}


def _text(event: dict[str, Any], key: str) -> str:
    value = event.get(key)
    return "" if value is None else str(value).strip().lower()


def _contains(event: dict[str, Any], value: str) -> bool:
    fields = [
        event.get("category"),
        event.get("description"),
        event.get("message"),
        event.get("rule_description"),
        event.get("alert"),
        event.get("classification"),
    ]

    haystack = " ".join(
        str(field).lower()
        for field in fields
        if field is not None
    )

    return value.lower() in haystack


def extract_features(event: dict[str, Any]) -> SecurityEventFeatures:
    source = _text(event, "source")
    severity = _text(event, "severity")

    severity_value = SEVERITY_MAP.get(severity, 0.10)
    category = _text(event, "category")

    http_status = event.get("http_status")

    try:
        http_status_int = int(http_status) if http_status is not None else 0
    except (TypeError, ValueError):
        http_status_int = 0

    try:
        destination_port = int(
            event.get("dst_port")
            or event.get("dest_port")
            or 0
        )
    except (TypeError, ValueError):
        destination_port = 0

    failed_auth = (
        _contains(event, "failed login")
        or _contains(event, "authentication failure")
        or _contains(event, "login failed")
        or _contains(event, "invalid password")
    )

    authentication_event = (
        _contains(event, "authentication")
        or _contains(event, "login")
        or _contains(event, "logon")
    )

    brute_force = (
        _contains(event, "brute force")
        or _contains(event, "password spraying")
        or _contains(event, "credential stuffing")
    )

    scanning = (
        _contains(event, "scan")
        or _contains(event, "reconnaissance")
        or _contains(event, "port scan")
    )

    sql_injection = (
        _contains(event, "sql injection")
        or _contains(event, "sqli")
    )

    xss = (
        _contains(event, "xss")
        or _contains(event, "cross-site scripting")
    )

    path_traversal = (
        _contains(event, "path traversal")
        or _contains(event, "directory traversal")
    )

    command_execution = (
        _contains(event, "command execution")
        or _contains(event, "command injection")
        or _contains(event, "powershell")
    )

    malware = (
        _contains(event, "malware")
        or _contains(event, "trojan")
    )

    credential_attack = (
        _contains(event, "credential attack")
        or _contains(event, "credential access")
        or _contains(event, "credential dumping")
    )

    data_exfiltration = (
        _contains(event, "exfiltration")
        or _contains(event, "data transfer")
    )

    suspicious_category = (
        category in SUSPICIOUS_CATEGORIES
        or any(
            [
                brute_force,
                scanning,
                sql_injection,
                xss,
                path_traversal,
                command_execution,
                malware,
                credential_attack,
                data_exfiltration,
            ]
        )
    )

    http_request = bool(
        event.get("url")
        or event.get("http_method")
        or event.get("http_status")
    )

    http_error = 400 <= http_status_int <= 599
    unusual_port = destination_port not in {0, 80, 443, 53}
    high_risk_port = destination_port in HIGH_RISK_PORTS

    return SecurityEventFeatures(
        severity=severity_value,
        source_is_suricata=float(source == "suricata"),
        source_is_wazuh=float(source == "wazuh"),
        source_is_cloudflare=float(source == "cloudflare"),
        source_is_web=float(
            source in {"web", "nginx", "apache", "application"}
        ),
        has_source_ip=float(bool(event.get("src_ip"))),
        has_destination_ip=float(
            bool(event.get("dst_ip") or event.get("dest_ip"))
        ),
        has_username=float(
            bool(event.get("username") or event.get("user"))
        ),
        has_hostname=float(bool(event.get("hostname"))),
        http_request=float(http_request),
        http_error=float(http_error),
        authentication_event=float(authentication_event),
        failed_authentication=float(failed_auth),
        suspicious_category=float(suspicious_category),
        brute_force=float(brute_force),
        scanning=float(scanning),
        sql_injection=float(sql_injection),
        xss=float(xss),
        path_traversal=float(path_traversal),
        command_execution=float(command_execution),
        malware=float(malware),
        credential_attack=float(credential_attack),
        data_exfiltration=float(data_exfiltration),
        unusual_port=float(unusual_port),
        high_risk_port=float(high_risk_port),
    )
