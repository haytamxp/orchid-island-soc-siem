"""
Gemini request isolation test.

This diagnostic separates:
1. Basic generation
2. System instructions
3. JSON structured output
4. Full SOC prompt
"""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.ai.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
)


load_dotenv(
    override=True
)


api_key = os.getenv(
    "GEMINI_API_KEY"
)

model = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


client = genai.Client(
    api_key=api_key
)


event = {
    "source": "manual",
    "description": (
        "Possible SQL injection attempt "
        "against a public web application."
    ),
    "severity": "High",
    "rule_id": "5710",
    "src_ip": "185.10.20.30",
    "dst_ip": "10.0.0.15",
    "hostname": "web-server",
    "url": (
        "/products?id=1 "
        "UNION SELECT username,password FROM users"
    ),
    "http_method": "GET",
    "http_status": 500,
}


def run_test(
    name: str,
    contents: str,
    system_instruction: str | None = None,
    json_mode: bool = False,
) -> None:

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    try:

        config_kwargs = {}

        if system_instruction:
            config_kwargs[
                "system_instruction"
            ] = system_instruction

        if json_mode:
            config_kwargs[
                "response_mime_type"
            ] = "application/json"

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                **config_kwargs
            ),
        )

        print("[SUCCESS] Response received.")

        if json_mode:

            parsed = json.loads(
                response.text
            )

            print(
                json.dumps(
                    parsed,
                    indent=2,
                    ensure_ascii=False,
                )
            )

        else:

            print(response.text)

    except Exception as exc:

        print("[FAILURE]")
        print(
            f"TYPE: {type(exc).__name__}"
        )

        print(
            f"ERROR: {exc}"
        )


# ============================================================
# TEST A
# ============================================================

run_test(
    "TEST A — BASIC GENERATION",
    (
        "Explain in one sentence "
        "what a SIEM does."
    ),
)


# ============================================================
# TEST B
# ============================================================

run_test(
    "TEST B — SYSTEM INSTRUCTION + JSON",
    "Return JSON containing one field named classification.",
    system_instruction=(
        "You are a SOC analyst. "
        "Return only JSON."
    ),
    json_mode=True,
)


# ============================================================
# TEST C
# ============================================================

run_test(
    "TEST C — FULL SOC SYSTEM PROMPT + SMALL EVENT",
    json.dumps(
        {
            "source": "manual",
            "description": "Possible SQL injection.",
            "severity": "High",
        },
        indent=2,
    ),
    system_instruction=SYSTEM_PROMPT,
    json_mode=True,
)


# ============================================================
# TEST D
# ============================================================

full_prompt = build_analysis_prompt(
    event
)

run_test(
    "TEST D — FULL SOC PROMPT + FULL EVENT",
    full_prompt,
    system_instruction=SYSTEM_PROMPT,
    json_mode=True,
)