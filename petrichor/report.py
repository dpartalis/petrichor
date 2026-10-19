"""Season summary reports built from the watering log."""

from pathlib import Path

import pandas as pd
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError

VERDICT_SKIP = "SKIP (rain coming)"
VERDICT_WATER = "WATER"


def load_log(log_path=None, delta_path=None):
    """Load the watering log as a DataFrame, from a Delta table or a CSV."""
    if delta_path:
        try:
            return DeltaTable(str(Path(delta_path))).to_pandas()
        except TableNotFoundError:
            raise FileNotFoundError(delta_path)
    return pd.read_csv(log_path)


def summarize(frame):
    """Build a per-zone summary of the watering log.

    Pure function: takes a DataFrame with the log columns, returns a list of
    row dicts ready for tabulate.
    """
    rows = []
    for zone, group in frame.groupby("zone"):
        group = group.sort_values("date")
        last = group.iloc[-1]
        verdicts = group["verdict"].value_counts()
        rows.append(
            {
                "zone": zone,
                "days_logged": len(group),
                "water_days": int(verdicts.get(VERDICT_WATER, 0)),
                "skip_days": int(verdicts.get(VERDICT_SKIP, 0)),
                "last_date": last["date"],
                "last_deficit_mm": round(float(last["deficit_mm"]), 1),
                "last_verdict": last["verdict"],
            }
        )
    return rows
