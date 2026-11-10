import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Project configuration
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY missing from .env file")

client = genai.Client(api_key=API_KEY)


def extract_json(text):
    """Extract JSON from Gemini response."""

    text = (text or "").strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Gemini did not return valid JSON.")

    return json.loads(text[start:end + 1])


def generate_post(slot="morning"):

    print(f"Generating {slot} herbal infographic with Gemini...")

    prompt = f"""
You are a professional herbal education content creator
for a Facebook page called Time To Herbs.

Create ONE original educational infographic about a herb,
spice, or medicinal plant.

Posting slot: {slot}

Return ONLY valid JSON using this structure:

{{
    "title": "Short attractive headline",
    "topic": "Name of the herb",
    "short_fact": "One interesting educational fact",
    "key_points": [
        "First educational point",
        "Second educational point",
        "Third educational point"
    ],
    "how_to_use": "One simple everyday kitchen tip",
    "safety_note": "A relevant safety warning",
    "caption": "An engaging Facebook caption",
    "hashtags": [
        "#TimeToHerbs",
        "#HerbalWisdom",
        "#HealthyLiving"
    ]
}}

CONTENT RULES:

1. Choose a common herb or plant.
2. Examples: Ginger, Turmeric, Mint, Basil,
   Cinnamon, Fennel, Rosemary, Garlic and Chamomile.
3. Create a short attractive headline.
4. Keep educational points concise.
5. Keep the short fact under 25 words.
6. Keep the usage tip under 25 words.
7. Keep the safety note concise.
8. Write an engaging Facebook caption.
9. Include relevant hashtags.

MEDICAL SAFETY:

- Never claim that herbs cure diseases.
- Never invent scientific research or statistics.
- Do not recommend replacing prescribed medicines.
- Distinguish traditional uses from proven benefits.
- Avoid unsupported medical claims.
- Include appropriate safety precautions.

Use simple English.
Do not use Markdown.
Return valid JSON only.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    data = extract_json(response.text)

    # Validate generated content

    data["title"] = str(
        data.get("title", "Herbal Wisdom")
    ).strip()

    data["topic"] = str(
        data.get("topic", "Herbal Education")
    ).strip()

    data["short_fact"] = str(
        data.get("short_fact", "")
    ).strip()

    data["key_points"] = [
        str(point).strip()
        for point in data.get("key_points", [])
        if str(point).strip()
    ][:3]

    while len(data["key_points"]) < 3:
        data["key_points"].append(
            "Learn about the plant before using it."
        )

    data["how_to_use"] = str(
        data.get("how_to_use", "")
    ).strip()

    data["safety_note"] = str(
        data.get(
            "safety_note",
            "Use herbs responsibly and seek professional advice when needed."
        )
    ).strip()

    data["caption"] = str(
        data.get("caption", "")
    ).strip()

    hashtags = data.get(
        "hashtags",
        ["#TimeToHerbs", "#HerbalWisdom"]
    )

    if isinstance(hashtags, str):
        hashtags = hashtags.split()

    data["hashtags"] = [
        str(tag).strip()
        for tag in hashtags
        if str(tag).strip()
    ]

    if "#TimeToHerbs" not in data["hashtags"]:
        data["hashtags"].insert(0, "#TimeToHerbs")

    # Compatibility with existing post.py
    data["quote"] = data["title"]

    data["caption"] += (
        "\n\n" + " ".join(data["hashtags"])
    )

    return data