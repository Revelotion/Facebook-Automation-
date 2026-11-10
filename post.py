#!/usr/bin/env python3

"""Generate and publish Time To Herbs Facebook content."""

import argparse
import json
import logging

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from ai_content import generate_post
from render import render_image

from facebook_api import (
    publish_photo,
    publish_story
)


HERE = Path(__file__).resolve().parent

OUT = HERE / "out"

STATE = HERE / "state.json"

LOG = HERE / "post.log"

PKT = ZoneInfo("Asia/Karachi")


# Logging configuration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(
            LOG,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)


def read_state():

    if STATE.exists():

        state = json.loads(
            STATE.read_text(encoding="utf-8")
        )

        state.setdefault("published_slots", {})

        return state

    return {
        "published_slots": {}
    }


def write_state(state):

    temp = STATE.with_suffix(".tmp")

    temp.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8"
    )

    temp.replace(STATE)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--slot",
        choices=["morning", "evening"],
        required=True
    )

    parser.add_argument(
        "--dry-run",
        action="store_true"
    )

    parser.add_argument(
        "--no-story",
        action="store_true"
    )

    args = parser.parse_args()

    # Pakistan time

    now = datetime.now(PKT)

    day = now.date().isoformat()

    slot_key = f"{day}:{args.slot}"

    state = read_state()

    # Prevent duplicate publishing

    if state["published_slots"].get(slot_key):

        logging.info(
            "Slot %s already completed for %s. Skipping.",
            args.slot,
            day
        )

        return

    # Generate content

    logging.info(
        "Generating %s herbal infographic with Gemini...",
        args.slot
    )

    content = generate_post(args.slot)

    stamp = now.strftime("%Y%m%d")

    seed = int(
        now.strftime("%Y%m%d")
    ) + (
        1 if args.slot == "morning" else 2
    )

    # Generate feed image

    feed_path = render_image(
        content,
        OUT / f"{stamp}_{args.slot}_feed.jpg",
        story=False,
        seed=seed
    )

    # Generate story image

    story_path = render_image(
        content,
        OUT / f"{stamp}_{args.slot}_story.jpg",
        story=True,
        seed=seed
    )

    # Facebook caption

    caption = (
        f"{content['topic']} | Herbal Education\n\n"
        f"{content['caption']}"
    )

    # Dry run

    if args.dry_run:

        print(
            json.dumps(
                content,
                indent=2,
                ensure_ascii=False
            )
        )

        print("\nFeed image:", feed_path)

        print("Story image:", story_path)

        print("\nDry run only: nothing was published.")

        return

    # Publish Facebook feed post

    post_id = publish_photo(
        feed_path,
        caption
    )

    logging.info(
        "Published Facebook Page photo post: %s",
        post_id
    )

    # Publish Facebook story

    if not args.no_story:

        try:

            story_id = publish_story(
                story_path
            )

            logging.info(
                "Published Facebook Page Story: %s",
                story_id
            )

        except Exception:

            logging.exception(
                "Story publishing failed. Feed post remains published."
            )

    # Save publishing state

    state["published_slots"][slot_key] = {

        "time": now.isoformat(),

        "post_id": post_id,

        "topic": content["topic"]

    }

    write_state(state)

    logging.info(
        "Finished slot %s.",
        args.slot
    )


if __name__ == "__main__":

    main()