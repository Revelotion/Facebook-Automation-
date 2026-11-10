#!/usr/bin/env python3
"""Minimal Facebook Pages Graph API publisher."""
import json
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"

def load_config():
    if not CONFIG.exists():
        raise RuntimeError("config.json not found. Copy config.example.json to config.json and configure your Page token.")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    for key in ("page_id", "page_access_token"):
        if not cfg.get(key) or "PASTE_" in str(cfg.get(key)):
            raise RuntimeError(f"Set '{key}' in config.json first.")
    return cfg

def graph_post(edge, data=None, files=None):
    cfg = load_config()
    version = cfg.get("graph_api_version", "v26.0")
    url = f"https://graph.facebook.com/{version}/{edge.lstrip('/')}"
    payload = dict(data or {})
    payload["access_token"] = cfg["page_access_token"]
    response = requests.post(url, data=payload, files=files, timeout=120)
    try:
        result = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError("Facebook returned a non-JSON response.")
    if not response.ok or "error" in result:
        raise RuntimeError(f"Facebook Graph API error: {result.get('error', result)}")
    return result

def publish_photo(image_path, caption):
    cfg = load_config()
    with open(image_path, "rb") as image:
        result = graph_post(
            f"{cfg['page_id']}/photos",
            data={"message": caption, "published": "true"},
            files={"source": (Path(image_path).name, image, "image/jpeg")},
        )
    return result.get("post_id") or result.get("id")

def publish_story(image_path):
    """Upload an unpublished Page photo, then create a Page photo Story."""
    cfg = load_config()
    with open(image_path, "rb") as image:
        uploaded = graph_post(
            f"{cfg['page_id']}/photos",
            data={"published": "false"},
            files={"source": (Path(image_path).name, image, "image/jpeg")},
        )
    photo_id = uploaded.get("id")
    if not photo_id:
        raise RuntimeError(f"Unpublished photo upload returned no photo ID: {uploaded}")
    story = graph_post(
        f"{cfg['page_id']}/photo_stories",
        data={"photo_id": photo_id},
    )
    return story.get("post_id") or story.get("id") or story
