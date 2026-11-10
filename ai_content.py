import os
import json
import re
import time
import logging

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
logger = logging.getLogger(__name__)

STATE_PATH = BASE_DIR / "state.json"

# A broad pool helps Gemini select varied subjects. The published history
# in state.json is the source of truth for avoiding recent repeats.
TOPIC_POOL = [
    "Garlic", "Rosemary", "Ginger", "Turmeric", "Mint", "Basil",
    "Cinnamon", "Fennel", "Chamomile", "Thyme", "Sage", "Oregano",
    "Lemongrass", "Clove", "Cardamom", "Coriander", "Parsley",
    "Dill", "Lavender", "Hibiscus", "Aloe Vera", "Lemon Balm",
    "Bay Leaf", "Black Pepper", "Cumin", "Fenugreek", "Ashwagandha",
    "Echinacea", "Calendula", "Moringa", "Nettle", "Dandelion",
    "Peppermint", "Anise", "Mustard", "Saffron", "Vanilla"
]


def extract_json(text):
    """Extract a JSON object from a Gemini response."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON object.")

    return json.loads(text[start:end + 1])


def is_temporary_error(exc):
    """Identify errors that may succeed on retry."""
    status = getattr(exc, "code", None)
    if status is None:
        status = getattr(exc, "status_code", None)

    response = getattr(exc, "response", None)
    if status is None and response is not None:
        status = getattr(response, "status_code", None)

    if status in (408, 429, 500, 502, 503, 504):
        return True

    message = str(exc).lower()
    temporary_codes = ("408", "429", "500", "502", "503", "504")
    temporary_messages = (
        "timeout", "timed out", "connection reset", "connection error",
        "temporarily unavailable", "service unavailable",
        "resource exhausted", "overloaded"
    )
    return (
        any(code in message for code in temporary_codes)
        or any(word in message for word in temporary_messages)
    )


def generate_with_retry(prompt):
    """Retry temporary Gemini errors with increasing delays."""
    delays = [5, 15, 30, 60]

    for attempt in range(5):
        try:
            logger.info("Gemini request attempt %s/5", attempt + 1)
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text

        except Exception as exc:
            if not is_temporary_error(exc) or attempt == 4:
                logger.exception("Gemini request failed.")
                raise

            wait = delays[attempt]
            logger.warning(
                "Temporary Gemini error: %s. Retrying in %s seconds.",
                exc, wait
            )
            time.sleep(wait)


def get_recent_topics(limit=30):
    """Read previously published topics from the existing state.json."""
    if not STATE_PATH.exists():
        return []

    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        slots = state.get("published_slots", {})
        topics = []

        # Keep the latest entries only.
        entries = sorted(
            slots.items(),
            key=lambda item: item[1].get("time", ""),
            reverse=True
        )

        for _, details in entries:
            topic = details.get("topic")
            if topic and topic.casefold() not in {
                item.casefold() for item in topics
            }:
                topics.append(str(topic).strip())

        return topics[:limit]

    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        logger.exception("Could not read topic history from state.json.")
        return []


def build_prompt(slot, recent_topics, avoid_extra=None):
    avoid = list(recent_topics)
    if avoid_extra:
        avoid.extend(avoid_extra)

    avoid_text = ", ".join(avoid) if avoid else "No published topic history yet."

    return f"""
You are the editorial and botanical education team for the Facebook page
Time To Herbs. Create one original, accurate, visually useful educational
infographic content package.

Posting slot: {slot}
Previously published topics to AVOID repeating: {avoid_text}

Choose a different herb, spice, edible plant, or garden plant. Do not use
a synonym, variety, or spelling variation of a topic in the avoid list.
Prefer a fresh topic not used recently. Morning content may focus on plant
identity, anatomy, growing, harvesting, or interesting facts. Evening
content may focus on culinary use, preparation, storage, history, or
botanical facts. Do not force a medical-benefit angle.

Return ONLY valid JSON in exactly this structure:
{{
  "title": "Short clear headline, ideally 4 to 9 words",
  "topic": "Common name of the plant",
  "short_fact": "One memorable factual sentence, maximum 22 words",
  "key_points": [
    "Concise educational fact or plant feature",
    "Concise growing, storage, history, or identification fact",
    "Another distinct useful fact"
  ],
  "how_to_use": "One practical, safe kitchen or gardening tip, maximum 24 words",
  "safety_note": "A concise, relevant caution. Do not invent a risk if none is relevant.",
  "caption": "A friendly, engaging Facebook caption of 2 to 4 short sentences.",
  "hashtags": ["#TimeToHerbs", "#HerbalWisdom", "#BotanicalEducation"],
  "visual_focus": "A short description of the most recognizable plant feature to illustrate",
  "plant_parts": ["Name of visible plant part", "Name of another visible part"],
  "growing_tips": ["Short growing tip", "Second short growing tip"]
}}

CONTENT AND DESIGN EDITORIAL RULES:
- Use simple, natural English and check spelling.
- Make facts specific to the chosen plant; do not recycle generic filler.
- Keep every point short enough to fit in a small infographic panel.
- Use plant anatomy, identification, growing, harvesting, storage,
  culinary uses, history, or culture where appropriate.
- Do not invent statistics, studies, citations, or scientific claims.
- Never claim that a plant or herb cures, treats, or prevents disease.
- Clearly distinguish traditional use from established evidence.
- Never advise replacing prescribed medicine.
- Do not give dosage instructions or make treatment recommendations.
- Safety notes should be relevant, proportionate, and factual.
- Return valid JSON only. No Markdown fences or commentary.
"""


def normalize_content(data):
    """Validate and normalize fields expected by render.py."""
    if not isinstance(data, dict):
        raise ValueError("Gemini JSON response must be an object.")

    required_text = ("title", "topic", "short_fact", "how_to_use", "safety_note", "caption")
    for key in required_text:
        data[key] = str(data.get(key, "")).strip()

    if not data["topic"] or not data["title"]:
        raise ValueError("Gemini response is missing its topic or title.")

    points = data.get("key_points", [])
    if not isinstance(points, list):
        points = []

    data["key_points"] = [
        str(point).strip() for point in points if str(point).strip()
    ][:3]

    while len(data["key_points"]) < 3:
        data["key_points"].append("Explore this plant and learn how it grows.")

    hashtags = data.get("hashtags", [])
    if isinstance(hashtags, str):
        hashtags = hashtags.split()
    if not isinstance(hashtags, list):
        hashtags = []

    data["hashtags"] = [
        str(tag).strip() for tag in hashtags if str(tag).strip()
    ]
    if "#TimeToHerbs" not in data["hashtags"]:
        data["hashtags"].insert(0, "#TimeToHerbs")

    data["visual_focus"] = str(data.get("visual_focus", data["topic"])).strip()

    for key in ("plant_parts", "growing_tips"):
        value = data.get(key, [])
        if not isinstance(value, list):
            value = []
        data[key] = [str(item).strip() for item in value if str(item).strip()][:3]

    data["quote"] = data["title"]
    hashtag_line = " ".join(data["hashtags"])
    if hashtag_line and hashtag_line not in data["caption"]:
        data["caption"] = data["caption"].rstrip() + "\n\n" + hashtag_line

    return data


def generate_post(slot="morning"):
    """Generate a fresh post while avoiding recently published topics."""
    logger.info("Generating %s herbal infographic with Gemini...", slot)

    recent = get_recent_topics(limit=30)
    recent_lower = {topic.casefold() for topic in recent}

    # Ask again if Gemini returns a topic already in the recent history.
    for content_attempt in range(1, 4):
        prompt = build_prompt(
            slot,
            recent,
            avoid_extra=TOPIC_POOL[:0]
        )
        raw_text = generate_with_retry(prompt)
        data = normalize_content(extract_json(raw_text))

        if data["topic"].casefold() not in recent_lower:
            logger.info("Selected new topic: %s", data["topic"])
            return data

        logger.warning(
            "Gemini repeated recent topic '%s' (content attempt %s/3).",
            data["topic"], content_attempt
        )
        recent.append(data["topic"])
        recent_lower.add(data["topic"].casefold())

    raise RuntimeError(
        "Gemini returned a recently published topic three times. "
        "No post was published; try the slot again later."
    )
