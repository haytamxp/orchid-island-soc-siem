"""
Temporary end-to-end test for the Gemini SOC analysis engine.
"""

from dotenv import load_dotenv

from backend.ai import (
    AIAnalyzer,
    GeminiClient,
    SecurityEvent,
)


def main():
    load_dotenv()

    event = SecurityEvent(
        source="manual",
        description=(
            "Possible SQL injection attempt "
            "against a public web application."
        ),
        severity="High",
        rule_id="5710",
        src_ip="185.10.20.30",
        dst_ip="10.0.0.15",
        hostname="web-server",
        url=(
            "/products?id=1 "
            "UNION SELECT username,password FROM users"
        ),
        http_method="GET",
        http_status=500,
    )

    client = GeminiClient()

    analyzer = AIAnalyzer(
        client=client
    )

    print("=" * 60)
    print("ORCHID ISLAND SOC/SIEM — AI TEST")
    print("=" * 60)

    print(
        f"[MODEL] {client.model}"
    )

    print(
        "[AI] Analyzing security event..."
    )

    analysis = analyzer.analyze(
        event
    )

    print()
    print("CLASSIFICATION:")
    print(
        analysis.classification
    )

    print()
    print("SEVERITY:")
    print(
        analysis.severity
    )

    print()
    print("CONFIDENCE:")
    print(
        analysis.confidence
    )

    print()
    print("SUMMARY:")
    print(
        analysis.summary
    )

    print()
    print("EVIDENCE:")

    for item in analysis.evidence:

        print(
            f"- [{item.category}] "
            f"{item.description} "
            f"(confidence={item.confidence:.2f})"
        )

    print()
    print("MITRE ATT&CK:")

    for technique in analysis.mitre_attack:

        print(
            f"- {technique.technique_id} "
            f"{technique.name}"
        )

    print()
    print("RECOMMENDED ACTIONS:")

    for action in analysis.recommended_actions:

        print(
            f"- {action}"
        )

    print()
    print("PLAYBOOK:")
    print(
        analysis.playbook
    )

    print()
    print("=" * 60)
    print("AI TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()