"""Record actual watering events and feed them into the balance model.

Watering is treated exactly like rain: it shrinks the soil water deficit.
Events are stored in a small CSV and merged into the weather series by date,
so events older than the replay window are ignored automatically.
"""

import csv
from pathlib import Path

EVENTS_COLUMNS = ["date", "zone", "amount_mm"]
DEFAULT_EVENTS_PATH = "data/watering_events.csv"


def append_event(events_path, date, zone, amount_mm):
    """Append one watering event to the CSV, creating it if necessary."""
    events_path = Path(events_path)
    events_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not events_path.exists()
    with events_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EVENTS_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({"date": date, "zone": zone, "amount_mm": amount_mm})


def load_events(events_path):
    """Return all watering events as a list of dicts ([] if no file yet)."""
    events_path = Path(events_path)
    if not events_path.exists():
        return []
    with events_path.open(newline="") as f:
        return list(csv.DictReader(f))


def apply_events(past, events, zone):
    """Merge one zone's watering events into the past weather series.

    Pure function: `past` is a list of daily weather dicts (date, et0_mm,
    precipitation_mm); returns (et0_mm, precipitation_mm + watered_mm) tuples
    in the same order. Events match by exact date and zone.
    """
    watered = {}
    for event in events:
        if event["zone"] == zone:
            watered[event["date"]] = watered.get(event["date"], 0.0) + float(
                event["amount_mm"]
            )
    return [
        (d["et0_mm"], d["precipitation_mm"] + watered.get(d["date"], 0.0))
        for d in past
    ]
