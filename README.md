# petrichor

*pe·tri·chor — the smell of earth after rain.*

**Know when *not* to water.** A tiny CLI that runs a FAO-style soil water
balance for your garden using free weather data (Open-Meteo — no API key,
no account). It tells you which plants actually need water today, and which
ones the sky is about to handle for you.

## How it works

1. You describe your garden in `plants.yaml`: a location and a set of zones,
   each with a `field_capacity_mm` (how much water the soil can hold) and a
   `water_threshold_mm` (how dry it may get before you act).
2. petrichor fetches the last 7 days of observed weather **and** the next
   7 days of forecast from [Open-Meteo](https://open-meteo.com/), including
   daily precipitation and FAO evapotranspiration (ET0).
3. It replays the past week through a bucket model per zone:
   `deficit += ET0 − precipitation`, clamped to `[0, field_capacity]`.
4. Verdict per zone:
   - **OK** — deficit below threshold, do nothing.
   - **SKIP (rain coming)** — deficit is high, but the next 2 days of
     forecast rain will cover it. Save the water.
   - **WATER** — deficit is high and no rain is coming.

Every run appends to `data/watering_log.csv`, so you build up a personal
watering time series for free.

## Example output

```
| date       | zone       |   deficit_mm |   rain_next_2d_mm | verdict   |
|------------|------------|--------------|-------------------|-----------|
| 2026-09-26 | tomatoes   |          7.7 |                 0 | OK        |
| 2026-09-26 | lawn       |          7.7 |                 0 | OK        |
| 2026-09-26 | succulents |          7.7 |                 0 | OK        |
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

The two numbers per zone are the whole game:

- `field_capacity_mm` — roughly how much plant-available water your soil
  holds. Sandy soil, pots, and shallow-rooted plants: low (20–30).
  Deep loam and lawns: higher (40–60).
- `water_threshold_mm` — how much deficit you tolerate before watering.
  Thirsty / drought-sensitive plants (tomatoes): low. Drought-tolerant
  plants (succulents, established shrubs): high.

Start with the example values and adjust after a week of watching the log.

## Tests

```bash
python -m pytest tests/ -v
```

## Stretch ideas

- `--delta` flag to append runs to a Delta Lake table via the `deltalake`
  Python package (no Spark needed) — turn the log into a queryable lakehouse.
- A `--simulate` mode that plays "what if no rain for 14 days" scenarios.
- Notifications (ntfy.sh is free and keyless) when a zone flips to WATER.

## License

MIT
