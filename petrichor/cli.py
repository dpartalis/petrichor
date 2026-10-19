"""petrichor command-line interface."""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

from tabulate import tabulate

from . import __version__
from .balance import decide, simulate
from .config import load_config
from .delta import append_delta
from .report import load_log, summarize
from .weather import fetch_daily, split_past_forecast

FORECAST_RAIN_WINDOW_DAYS = 2
DEFAULT_DELTA_PATH = "data/watering_log_delta"


def run(config_path, log_path, delta_path=None):
    cfg = load_config(config_path)
    loc = cfg["location"]

    days = fetch_daily(
        loc["latitude"],
        loc["longitude"],
        timezone=loc.get("timezone", "auto"),
    )
    today = date.today().isoformat()
    past, forecast = split_past_forecast(days, today)
    forecast_rain_mm = sum(
        d["precipitation_mm"] for d in forecast[:FORECAST_RAIN_WINDOW_DAYS]
    )

    rows = []
    for zone in cfg["zones"]:
        series = [(d["et0_mm"], d["precipitation_mm"]) for d in past]
        deficits = simulate(
            0.0,
            series,
            zone["field_capacity_mm"],
            crop_coefficient=zone.get("crop_coefficient", 1.0),
        )
        deficit = deficits[-1] if deficits else 0.0
        verdict = decide(deficit, zone["water_threshold_mm"], forecast_rain_mm)
        rows.append(
            {
                "date": today,
                "zone": zone["name"],
                "deficit_mm": round(deficit, 1),
                "rain_next_2d_mm": round(forecast_rain_mm, 1),
                "verdict": verdict,
            }
        )

    _append_log(log_path, rows)
    if delta_path:
        append_delta(delta_path, rows)
    print(tabulate(rows, headers="keys", tablefmt="github"))
    print(f"\nLog appended to {log_path}")
    if delta_path:
        print(f"Delta table appended to {delta_path}")


def _append_log(log_path, rows):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_path.exists()
    with log_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["report"]:
        report(argv[1:])
        return
    parser = argparse.ArgumentParser(
        prog="petrichor",
        description="Know when not to water — a soil water balance for your garden.",
    )
    parser.add_argument("--config", default="plants.yaml", help="path to plants.yaml")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--log", default="data/watering_log.csv", help="path to the watering log CSV"
    )
    parser.add_argument(
        "--delta",
        nargs="?",
        const=DEFAULT_DELTA_PATH,
        metavar="PATH",
        help=f"also append to a Delta table (default: {DEFAULT_DELTA_PATH})",
    )
    args = parser.parse_args(argv)
    run(args.config, args.log, args.delta)


def report(argv):
    parser = argparse.ArgumentParser(
        prog="petrichor report",
        description="Summarize the watering log per zone.",
    )
    parser.add_argument(
        "--log", default="data/watering_log.csv", help="path to the watering log CSV"
    )
    parser.add_argument(
        "--delta",
        nargs="?",
        const=DEFAULT_DELTA_PATH,
        metavar="PATH",
        help=f"read the Delta table instead of the CSV (default: {DEFAULT_DELTA_PATH})",
    )
    args = parser.parse_args(argv)
    try:
        frame = load_log(
            log_path=None if args.delta else args.log, delta_path=args.delta
        )
    except FileNotFoundError:
        raise SystemExit(
            f"No watering log found at {args.delta or args.log} — run petrichor first."
        )
    print(tabulate(summarize(frame), headers="keys", tablefmt="github"))


if __name__ == "__main__":
    main()
