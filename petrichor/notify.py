"""Push notifications via ntfy.sh (free, no account, one HTTP POST)."""

import requests

NTFY_URL = "https://ntfy.sh"


def find_flips(previous_rows, current_rows):
    """Return zones whose verdict flipped to WATER since the last logged run.

    Pure function. A zone that has never been logged before does not count as
    a flip, and staying WATER across runs does not re-notify.
    """
    last_verdict = {}
    for row in previous_rows:
        last_verdict[row["zone"]] = row["verdict"]
    return [
        row["zone"]
        for row in current_rows
        if row["verdict"] == "WATER" and last_verdict.get(row["zone"]) not in (None, "WATER")
    ]


def send_ntfy(topic, title, body):
    """POST a notification to an ntfy.sh topic.

    Network failures print a warning instead of crashing the run.
    """
    try:
        resp = requests.post(
            f"{NTFY_URL}/{topic}",
            data=body.encode("utf-8"),
            headers={"Title": title},
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"Warning: notification to ntfy.sh/{topic} failed: {exc}")
        return False
    return True
