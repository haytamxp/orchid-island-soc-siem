"""
Minimal Gemini model and generation diagnostic.
"""

import os

from dotenv import load_dotenv
from google import genai


load_dotenv(
    override=True
)

api_key = os.getenv(
    "GEMINI_API_KEY"
)

model = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )

print("=" * 60)
print("GEMINI GENERATION TEST")
print("=" * 60)

print(
    f"[MODEL] {model}"
)

print(
    "[KEY] API key configured: True"
)

client = genai.Client(
    api_key=api_key
)

print(
    "[TEST] Querying model metadata..."
)

model_info = client.models.get(
    model=model
)

print(
    "[SUCCESS] Model accessible."
)

print(
    f"[MODEL NAME] {model_info.name}"
)

print()
print(
    "[TEST] Sending minimal generation request..."
)

try:

    response = client.models.generate_content(
        model=model,
        contents=(
            "In one sentence, explain "
            "what a SIEM does."
        ),
    )

    print()
    print(
        "[SUCCESS] Gemini responded."
    )

    print()
    print(
        "RESPONSE:"
    )

    print(
        response.text
    )

except Exception as exc:

    print()
    print(
        "[FAILURE] Gemini generation failed."
    )

    print(
        f"TYPE: {type(exc).__name__}"
    )

    print(
        f"ERROR: {exc}"
    )

print("=" * 60)