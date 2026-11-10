
#!/usr/bin/env python3

"""Schedule two daily Facebook posts for Time To Herbs."""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = sys.executable
SCRIPT = HERE / "post.py"

TASKS = [
    ("TimeToHerbs_Morning_1000", "morning", "10:00"),
    ("TimeToHerbs_Evening_2000", "evening", "20:00"),
]


def create_task(name, slot, time):
    command = f'"{PYTHON}" "{SCRIPT}" --slot {slot}'

    args = [
        "schtasks",
        "/Create",
        "/F",
        "/SC", "DAILY",
        "/TN", name,
        "/ST", time,
        "/TR", command,
        "/IT",
    ]

    print(f"\nCreating {name} at {time}...")

    result = subprocess.run(
        args,
        text=True,
        capture_output=True
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(f"Failed to create task: {name}")

    print(result.stdout.strip())
    print(f"SUCCESS: {name}")


def main():
    print("=" * 50)
    print("TIME TO HERBS - FACEBOOK AUTOMATION")
    print("=" * 50)

    if not SCRIPT.exists():
        raise SystemExit("post.py not found in project folder.")

    print("Python:", PYTHON)
    print("Project:", HERE)
    print("\nSchedule: Pakistan Standard Time")
    print("Morning: 10:00 AM")
    print("Evening: 8:00 PM")

    for name, slot, time in TASKS:
        create_task(name, slot, time)

    print("\n" + "=" * 50)
    print("BOTH DAILY TASKS CREATED SUCCESSFULLY!")
    print("=" * 50)
    print("\nOpen Task Scheduler to inspect or test them.")
    print("Your computer must be awake and your Windows")
    print("account must be logged in at publishing time.")


if __name__ == "__main__":
    main()
