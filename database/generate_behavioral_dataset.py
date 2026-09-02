"""
Generate a chronological behavioral security dataset.

Unlike an isolated-event generator, this creates event sequences:
- normal user activity
- login-failure bursts
- port scanning
- web attack bursts
- malware/process activity
- credential attacks
- data-exfiltration bursts

The generated data intentionally contains overlap between benign and
malicious traffic so the classifier cannot rely on one deterministic field.
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


SEED = 20260902
random.seed(SEED)

OUTPUT = Path(
    "database/ml_training_dataset_behavioral.csv"
)

ROW_COUNT = 12000

START_TIME = datetime(
    2026,
    1,
    1,
    0,
    0,
    0,
)

USERS = [
    "alice",
    "bob",
    "charlie",
    "david",
    "emma",
    "fatima",
    "admin",
    "analyst",
    "service_web",
]

HOSTS = [
    "web01",
    "web02",
    "app01",
    "db01",
    "mail01",
    "proxy01",
]

NORMAL_PATHS = [
    "/",
    "/properties",
    "/fr/properties",
    "/en/properties",
    "/properties/123",
    "/properties/456",
    "/search",
    "/contact",
    "/about",
    "/services",
    "/login",
    "/logout",
    "/api/properties",
    "/api/search",
    "/assets/app.js",
    "/assets/app.css",
    "/images/house.jpg",
    "/robots.txt",
    "/sitemap.xml",
]

WEB_ATTACK_PATHS = [
    "/properties?id=1'",
    "/properties?id=1+UNION+SELECT",
    "/search?q=<script>alert(1)</script>",
    "/search?q=%3Cscript%3E",
    "/../../etc/passwd",
    "/..%2f..%2fetc%2fpasswd",
    "/api?cmd=whoami",
    "/api?exec=id",
    "/admin/login",
    "/.env",
    "/config.php",
]

GENERIC_DESCRIPTIONS = [
    "Normal application request",
    "Application security event",
    "Request rejected by policy",
    "Unusual request pattern",
    "Network event observed",
    "Authentication event",
    "Application returned an error",
    "Endpoint activity observed",
]

MALICIOUS_DESCRIPTIONS = [
    "Request blocked by security policy",
    "Abnormal authentication activity",
    "Unusual network behavior observed",
    "Endpoint security event",
    "Outbound transfer anomaly",
    "Repeated connection failures",
    "Suspicious application activity",
    "Security rule triggered",
]

SOURCES = [
    "web",
    "wazuh",
    "suricata",
    "cloudflare",
]

FIELDS = [
    "timestamp",
    "severity",
    "source",
    "category",
    "description",
    "src_ip",
    "dst_ip",
    "dst_port",
    "username",
    "hostname",
    "url",
    "http_method",
    "http_status",
    "bytes_in",
    "bytes_out",
    "action",
    "event_id",
    "label",
]


def random_external_ip() -> str:
    return (
        f"{random.randint(11, 223)}."
        f"{random.randint(0, 255)}."
        f"{random.randint(0, 255)}."
        f"{random.randint(1, 254)}"
    )


def random_internal_ip() -> str:
    return (
        f"10.0."
        f"{random.randint(1, 30)}."
        f"{random.randint(1, 254)}"
    )


def base_event(
    timestamp: datetime,
    *,
    label: int,
    source: str,
    src_ip: str,
    dst_ip: str,
    dst_port: int,
    severity: str,
    category: str,
    description: str,
    username: str = "",
    hostname: str = "",
    url: str = "",
    http_method: str = "",
    http_status: int = 0,
    bytes_in: float = 0.0,
    bytes_out: float = 0.0,
    action: str = "",
    event_id: str = "",
) -> dict:
    return {
        "timestamp": timestamp.isoformat(),
        "severity": severity,
        "source": source,
        "category": category,
        "description": description,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "dst_port": dst_port,
        "username": username,
        "hostname": hostname,
        "url": url,
        "http_method": http_method,
        "http_status": http_status,
        "bytes_in": round(bytes_in, 2),
        "bytes_out": round(bytes_out, 2),
        "action": action,
        "event_id": event_id,
        "label": label,
    }


def normal_event(
    timestamp: datetime,
    sequence_id: int,
    step: int,
) -> dict:
    source = random.choices(
        SOURCES,
        weights=[42, 28, 10, 20],
        k=1,
    )[0]

    src_ip = random_external_ip()
    dst_ip = "10.0.0.10"
    username = random.choice(USERS)
    hostname = random.choice(HOSTS)

    if source in {"web", "cloudflare"}:
        method = random.choices(
            ["GET", "POST", "PUT"],
            weights=[82, 15, 3],
            k=1,
        )[0]

        status = random.choices(
            [200, 201, 301, 302, 400, 404, 403, 429, 500],
            weights=[64, 5, 7, 5, 4, 5, 3, 1, 6],
            k=1,
        )[0]

        return base_event(
            timestamp,
            label=0,
            source=source,
            src_ip=src_ip,
            dst_ip=dst_ip,
            dst_port=443,
            severity=random.choices(
                ["low", "medium", "high"],
                weights=[74, 23, 3],
                k=1,
            )[0],
            category=random.choice(
                [
                    "web_access",
                    "web_error",
                    "waf_event",
                ]
            ),
            description=random.choice(
                GENERIC_DESCRIPTIONS
            ),
            username=username,
            hostname=hostname,
            url=random.choice(NORMAL_PATHS),
            http_method=method,
            http_status=status,
            bytes_in=random.uniform(200, 5000),
            bytes_out=random.uniform(100, 25000),
            action=random.choice(
                ["allowed", "logged", "served"]
            ),
            event_id=f"n-{sequence_id}-{step}",
        )

    return base_event(
        timestamp,
        label=0,
        source=source,
        src_ip=src_ip,
        dst_ip=dst_ip,
        dst_port=random.choice(
            [22, 53, 80, 443, 3306]
        ),
        severity=random.choices(
            ["low", "medium", "high"],
            weights=[72, 25, 3],
            k=1,
        )[0],
        category=random.choice(
            [
                "authentication",
                "system",
                "network",
                "process",
            ]
        ),
        description=random.choice(
            [
                "Normal login event",
                "Successful user authentication",
                "Normal network connection",
                "Normal process activity",
                "Scheduled maintenance",
                "Normal database connection",
            ]
        ),
        username=username,
        hostname=hostname,
        bytes_in=random.uniform(100, 5000),
        bytes_out=random.uniform(50, 10000),
        action=random.choice(
            ["allowed", "success", "logged"]
        ),
        event_id=f"n-{sequence_id}-{step}",
    )


def benign_lookalike(
    timestamp: datetime,
    sequence_id: int,
    step: int,
) -> dict:
    """
    Benign activity intentionally resembling suspicious activity.
    """

    src_ip = random_external_ip()

    scenario = random.choice(
        [
            "authorized_scan",
            "waf_burst",
            "failed_login_then_success",
            "large_transfer",
        ]
    )

    if scenario == "authorized_scan":
        return base_event(
            timestamp,
            label=0,
            source="suricata",
            src_ip=src_ip,
            dst_ip="10.0.0.10",
            dst_port=random.choice(
                [
                    22,
                    53,
                    80,
                    443,
                    445,
                    3389,
                    8080,
                ]
            ),
            severity="medium",
            category="network",
            description="Approved vulnerability scan",
            username="analyst",
            hostname="scanner01",
            action="allowed",
            event_id=f"b-{sequence_id}-{step}",
        )

    if scenario == "waf_burst":
        return base_event(
            timestamp,
            label=0,
            source="cloudflare",
            src_ip=src_ip,
            dst_ip="10.0.0.10",
            dst_port=443,
            severity="high",
            category="waf_event",
            description="WAF challenge for automated client",
            username="",
            hostname="web01",
            url=random.choice(NORMAL_PATHS),
            http_method="GET",
            http_status=429,
            bytes_in=1000,
            bytes_out=500,
            action="challenged",
            event_id=f"b-{sequence_id}-{step}",
        )

    if scenario == "failed_login_then_success":
        return base_event(
            timestamp,
            label=0,
            source="wazuh",
            src_ip=src_ip,
            dst_ip="10.0.0.20",
            dst_port=22,
            severity="medium",
            category="authentication",
            description=random.choice(
                [
                    "Failed login attempt",
                    "Invalid password",
                ]
            ),
            username=random.choice(USERS),
            hostname="app01",
            action="failed",
            event_id=f"b-{sequence_id}-{step}",
        )

    return base_event(
        timestamp,
        label=0,
        source="web",
        src_ip=src_ip,
        dst_ip="10.0.0.10",
        dst_port=443,
        severity="medium",
        category="web_access",
        description="Scheduled application export",
        username="analyst",
        hostname="app01",
        url="/api/export",
        http_method="POST",
        http_status=200,
        bytes_in=random.uniform(500, 3000),
        bytes_out=random.uniform(2_000_000, 12_000_000),
        action="allowed",
        event_id=f"b-{sequence_id}-{step}",
    )


def attack_sequence(
    start: datetime,
    sequence_id: int,
) -> list[dict]:
    attack_type = random.choice(
        [
            "BRUTE_FORCE",
            "SCANNING",
            "WEB_ATTACK",
            "MALWARE",
            "CREDENTIAL_ATTACK",
            "DATA_EXFILTRATION",
        ]
    )

    src_ip = random_external_ip()
    dst_ip = random.choice(
        [
            "10.0.0.10",
            "10.0.0.20",
            "10.0.0.30",
        ]
    )

    events: list[dict] = []

    if attack_type == "BRUTE_FORCE":
        for step in range(
            random.randint(8, 16)
        ):
            events.append(
                base_event(
                    start + timedelta(
                        seconds=step * random.randint(3, 12)
                    ),
                    label=1,
                    source=random.choice(
                        ["wazuh", "suricata", "web"]
                    ),
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    dst_port=random.choice(
                        [22, 3389, 443]
                    ),
                    severity=random.choice(
                        ["medium", "high", "critical"]
                    ),
                    category="authentication",
                    description=random.choice(
                        [
                            "Authentication anomaly",
                            "Repeated connection failure",
                            "Security event observed",
                        ]
                    ),
                    username=random.choice(USERS),
                    hostname=random.choice(HOSTS),
                    action="failed",
                    event_id=f"a-{sequence_id}-{step}",
                )
            )

    elif attack_type == "SCANNING":
        ports = random.sample(
            [
                21,
                22,
                23,
                25,
                53,
                80,
                110,
                139,
                443,
                445,
                1433,
                3306,
                3389,
                5432,
                5985,
                8080,
            ],
            k=random.randint(8, 14),
        )

        for step, port in enumerate(ports):
            events.append(
                base_event(
                    start + timedelta(
                        seconds=step * random.randint(2, 8)
                    ),
                    label=1,
                    source=random.choice(
                        [
                            "suricata",
                            "wazuh",
                        ]
                    ),
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    dst_port=port,
                    severity=random.choice(
                        ["medium", "high"]
                    ),
                    category="network",
                    description=random.choice(
                        [
                            "Network discovery pattern detected",
                            "Unusual network probing observed",
                            "Multiple connection attempts",
                            "Network event observed",
                        ]
                    ),
                    hostname=random.choice(HOSTS),
                    action="observed",
                    event_id=f"a-{sequence_id}-{step}",
                )
            )

    elif attack_type == "WEB_ATTACK":
        for step in range(
            random.randint(6, 12)
        ):
            path = random.choice(
                WEB_ATTACK_PATHS
            )

            events.append(
                base_event(
                    start + timedelta(
                        seconds=step * random.randint(5, 15)
                    ),
                    label=1,
                    source=random.choice(
                        [
                            "web",
                            "cloudflare",
                            "suricata",
                        ]
                    ),
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    dst_port=443,
                    severity=random.choice(
                        [
                            "medium",
                            "high",
                            "critical",
                        ]
                    ),
                    category=random.choice(
                        [
                            "web_request",
                            "waf_event",
                            "application",
                        ]
                    ),
                    description=random.choice(
                        MALICIOUS_DESCRIPTIONS
                    ),
                    username=random.choice(USERS),
                    hostname="web01",
                    url=path,
                    http_method=random.choice(
                        ["GET", "POST"]
                    ),
                    http_status=random.choice(
                        [
                            403,
                            404,
                            429,
                            500,
                        ]
                    ),
                    bytes_in=random.uniform(
                        100,
                        5000,
                    ),
                    bytes_out=random.uniform(
                        100,
                        5000,
                    ),
                    action="blocked",
                    event_id=f"a-{sequence_id}-{step}",
                )
            )

    elif attack_type == "MALWARE":
        for step in range(
            random.randint(4, 8)
        ):
            events.append(
                base_event(
                    start + timedelta(
                        seconds=step * random.randint(10, 40)
                    ),
                    label=1,
                    source="wazuh",
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    dst_port=random.choice(
                        [80, 443, 8080]
                    ),
                    severity=random.choice(
                        ["high", "critical"]
                    ),
                    category="process",
                    description=random.choice(
                        MALICIOUS_DESCRIPTIONS
                    ),
                    username=random.choice(USERS),
                    hostname=random.choice(HOSTS),
                    bytes_out=random.uniform(
                        1000,
                        300000,
                    ),
                    action="detected",
                    event_id=f"a-{sequence_id}-{step}",
                )
            )

    elif attack_type == "CREDENTIAL_ATTACK":
        for step in range(
            random.randint(5, 10)
        ):
            events.append(
                base_event(
                    start + timedelta(
                        seconds=step * random.randint(4, 20)
                    ),
                    label=1,
                    source="wazuh",
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    dst_port=random.choice(
                        [88, 389, 445, 3389]
                    ),
                    severity=random.choice(
                        ["high", "critical"]
                    ),
                    category="authentication",
                    description=random.choice(
                        MALICIOUS_DESCRIPTIONS
                    ),
                    username=random.choice(USERS),
                    hostname=random.choice(HOSTS),
                    action=random.choice(
                        [
                            "failed",
                            "denied",
                            "detected",
                        ]
                    ),
                    event_id=f"a-{sequence_id}-{step}",
                )
            )

    else:
        for step in range(
            random.randint(4, 7)
        ):
            events.append(
                base_event(
                    start + timedelta(
                        seconds=step * random.randint(15, 40)
                    ),
                    label=1,
                    source=random.choice(
                        [
                            "wazuh",
                            "suricata",
                            "web",
                        ]
                    ),
                    src_ip=src_ip,
                    dst_ip=random.choice(
                        [
                            dst_ip,
                            random_external_ip(),
                        ]
                    ),
                    dst_port=random.choice(
                        [
                            80,
                            443,
                            8080,
                        ]
                    ),
                    severity=random.choice(
                        ["high", "critical"]
                    ),
                    category="network",
                    description=random.choice(
                        MALICIOUS_DESCRIPTIONS
                    ),
                    username=random.choice(USERS),
                    hostname=random.choice(HOSTS),
                    url=random.choice(
                        NORMAL_PATHS
                    ),
                    http_method="POST",
                    http_status=200,
                    bytes_in=random.uniform(
                        1000,
                        10000,
                    ),
                    bytes_out=random.uniform(
                        2_000_000,
                        40_000_000,
                    ),
                    action="allowed",
                    event_id=f"a-{sequence_id}-{step}",
                )
            )

    return events


rows: list[dict] = []
current_time = START_TIME
sequence_id = 0

while len(rows) < ROW_COUNT:
    sequence_id += 1

    # Gap between behavioral episodes.
    current_time += timedelta(
        seconds=random.randint(
            30,
            1800,
        )
    )

    scenario = random.random()

    if scenario < 0.14:
        sequence = attack_sequence(
            current_time,
            sequence_id,
        )
    elif scenario < 0.25:
        sequence = [
            benign_lookalike(
                current_time
                + timedelta(
                    seconds=step * random.randint(5, 20)
                ),
                sequence_id,
                step,
            )
            for step in range(
                random.randint(2, 8)
            )
        ]
    else:
        sequence = [
            normal_event(
                current_time
                + timedelta(
                    seconds=step * random.randint(10, 120)
                ),
                sequence_id,
                step,
            )
            for step in range(
                random.randint(1, 8)
            )
        ]

    rows.extend(sequence)

    if sequence:
        current_time = datetime.fromisoformat(
            sequence[-1]["timestamp"]
        )

rows = rows[:ROW_COUNT]

# Small amount of label noise.
for row in rows:
    if random.random() < 0.012:
        row["label"] = 1 - row["label"]

rows.sort(
    key=lambda row: row["timestamp"]
)

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with OUTPUT.open(
    "w",
    encoding="utf-8",
    newline="",
) as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=FIELDS,
    )
    writer.writeheader()
    writer.writerows(rows)

benign = sum(
    row["label"] == 0
    for row in rows
)

malicious = sum(
    row["label"] == 1
    for row in rows
)

print(f"Generated: {OUTPUT}")
print(f"Rows: {len(rows)}")
print(f"Benign: {benign}")
print(f"Malicious: {malicious}")
print(
    f"Malicious ratio: "
    f"{malicious / len(rows):.2%}"
)
print(
    f"First timestamp: "
    f"{rows[0]['timestamp']}"
)
print(
    f"Last timestamp: "
    f"{rows[-1]['timestamp']}"
)
