#!/usr/bin/env python3
"""Local helper: exchange a short-lived User token and save the selected Page token."""
import getpass
import json
from pathlib import Path
import requests

GRAPH = "https://graph.facebook.com/v26.0"
HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"

def graph_get(path, **params):
    response = requests.get(f"{GRAPH}/{path.lstrip('/')}", params=params, timeout=45)
    data = response.json()
    if not response.ok or "error" in data:
        raise RuntimeError(data.get("error", data))
    return data

def main():
    print("Enter credentials locally in this terminal. Do not paste them into a chat.")
    app_id = input("Meta App ID: ").strip()
    app_secret = getpass.getpass("Meta App Secret (hidden): ").strip()
    short_token = getpass.getpass("Short-lived User Access Token (hidden): ").strip()

    print("Exchanging User token...")
    long_user = graph_get(
        "oauth/access_token",
        grant_type="fb_exchange_token",
        client_id=app_id,
        client_secret=app_secret,
        fb_exchange_token=short_token,
    )["access_token"]

    print("Loading Pages available to this account...")
    pages = graph_get("me/accounts", access_token=long_user,
                      fields="id,name,access_token,tasks").get("data", [])
    if not pages:
        raise SystemExit("No Pages returned. Check Page access and permissions.")

    for index, page in enumerate(pages, 1):
        print(f"{index}. {page['name']} (Page ID: {page['id']})")
    choice = int(input("Enter the number for Time To Herbs: ")) - 1
    if choice < 0 or choice >= len(pages):
        raise SystemExit("Invalid selection.")
    page = pages[choice]

    CONFIG.write_text(json.dumps({
        "page_id": page["id"],
        "page_name": page["name"],
        "page_access_token": page["access_token"],
        "graph_api_version": "v26.0",
    }, indent=2), encoding="utf-8")
    try:
        CONFIG.chmod(0o600)
    except OSError:
        pass
    print(f"Saved Page token locally to {CONFIG}. Keep config.json private.")
    print("A Page token can still be revoked or invalidated; check it if publishing stops.")

if __name__ == "__main__":
    main()
