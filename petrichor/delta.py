"""Write watering history to Delta Lake tables."""

from pathlib import Path

import pandas as pd
from deltalake import write_deltalake

LOG_COLUMNS = ["date", "zone", "deficit_mm", "rain_next_2d_mm", "verdict"]


def append_delta(delta_path, rows):
    """Append one run's rows to a Delta table, creating it if necessary."""
    delta_path = Path(delta_path)
    delta_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=LOG_COLUMNS)
    write_deltalake(str(delta_path), frame, mode="append")
