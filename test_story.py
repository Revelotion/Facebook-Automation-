from pathlib import Path
from facebook_api import publish_story

image = Path("out/20261108_morning_story.jpg")

if not image.exists():
    raise FileNotFoundError(image)

story_id = publish_story(image)

print("Facebook Story published successfully!")
print("Story ID:", story_id)