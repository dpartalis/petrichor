# petrichor

*pe·tri·chor — the smell of earth after rain.*

**Know when *not* to water.** A tiny CLI that runs a FAO-style soil water
balance for your garden using free weather data (Open-Meteo — no API key,
no account). It tells you which plants actually need water today, and which
ones the sky is about to handle for you.

## How it works

1. You describe your garden in `plants.yaml`: a location and a set of zones,
   each with a `field_capacity_mm` (how much water the soil can hold), a
   `water_threshold_mm` (how dry it may get before you act), and an optional
   crop coefficient.
2. petrichor fetches the last 7 days of observed weather **and** the next
   7 days of forecast from [Open-Meteo](https://open-meteo.com/), including
   daily precipitation and FAO evapotranspiration (ET0).
3. It replays the past week through a bucket model per zone:
   `deficit += ET0 × crop_coefficient − precipitation`, clamped to
   `[0, field_capacity]`.
4. Verdict per zone:
   - **OK** — deficit below threshold, do nothing.
   - **SKIP (rain coming)** — deficit is high, but the next 2 days of
     forecast rain will cover it. Save the water.
   - **WATER** — deficit is high and no rain is coming.

Every run appends to `data/watering_log.csv`, so you build up a personal
watering time series for free. Add `--delta` to append the same run to a
Delta Lake table.

## Example output

```
| date       | zone       |   deficit_mm |   rain_next_2d_mm | verdict   |
|------------|------------|--------------|-------------------|-----------|
| 2026-09-26 | tomatoes   |          8.9 |                 0 | OK        |
| 2026-09-26 | lawn       |          6.2 |                 0 | OK        |
| 2026-09-26 | succulents |          2.3 |                 0 | OK        |
```

## Install & run

```bash
git clone https://github.com/dpartalis/petrichor.git
cd petrichor
pip install -r requirements.txt

cp plants.example.yaml plants.yaml   # then edit coordinates & zones
python -m petrichor --config plants.yaml
```

Or install it as a package to get a `petrichor` command:

```bash
pip install .
petrichor --config plants.yaml
```

## Configuring zones

- `field_capacity_mm` — roughly how much plant-available water your soil
  holds. Sandy soil, pots, and shallow-rooted plants: low (20–30).
  Deep loam and lawns: higher (40–60).
- `water_threshold_mm` — how much deficit you tolerate before watering.
  Thirsty / drought-sensitive plants (tomatoes): low. Drought-tolerant
  plants (succulents, established shrubs): high.
- `crop_coefficient` — optional crop-specific ET0 multiplier (Kc), defaulting
  to `1.0`. Starting points include tomatoes at `1.15`, lawn at `0.8`, and
  succulents at `0.3`.

Start with the example values and adjust after a week of watching the log.

## Delta Lake logging

Use `--delta` to append each run to `data/watering_log_delta` as well as the
CSV, or pass a custom table path:

```bash
petrichor --config plants.yaml --delta
petrichor --config plants.yaml --delta data/my_watering_table
```

No Spark or Docker is required. Each append creates a Delta table version,
so you can query current history or time-travel to an earlier run:

```python
from deltalake import DeltaTable

history = DeltaTable("data/watering_log_delta").to_pandas()
first_run = DeltaTable("data/watering_log_delta", version=0).to_pandas()
```

## Daily GitHub Action

`.github/workflows/daily.yml` runs at 05:17 UTC every morning and can also be
started manually. It appends both log formats and commits the changes back to
the repository. The workflow uses `plants.yaml` when that file is present and
falls back to `plants.example.yaml`.

To use your own garden in Actions, track `plants.yaml` (for example with
`git add -f plants.yaml`) or edit the workflow's config path. On a public
repository, tracking the config also publishes its coordinates.

## Contributing

This project uses a lightweight Conventional Commits style — see `COMMITS.md`.

## Tests

```bash
python -m pytest tests/ -v
```

## Stretch ideas

- A `--simulate` mode that plays "what if no rain for 14 days" scenarios.
- Notifications (ntfy.sh is free and keyless) when a zone flips to WATER.

## License

MIT
