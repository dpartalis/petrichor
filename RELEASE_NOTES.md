# Release notes

## 0.2.0 — 2026-10-18

This release adds Delta Lake history, crop-specific evapotranspiration, and automated daily watering-log updates. Existing YAML configurations and CSV-only commands remain compatible.

### Delta Lake logging

- Added `--delta` to append each run to `data/watering_log_delta` while continuing to write the CSV log.
- Added `--delta PATH` for custom Delta table locations.
- Delta tables use the native `deltalake` Python package; Spark and Docker are not required.
- Each append creates a new table version, supporting `DeltaTable.to_pandas()` queries and time travel to earlier versions.

```powershell
python -m petrichor --config plants.yaml --delta
python -m petrichor --config plants.yaml --delta data\my_watering_table
```

### Crop coefficients

- Added an optional `crop_coefficient` (Kc) field for each zone.
- The water-balance model now calculates crop water use as `ET0 × crop_coefficient`.
- Existing configurations default to `1.0`, preserving their previous behavior.
- Example configurations now include tomatoes at `1.15`, lawn at `0.8`, and succulents at `0.3`.

```yaml
zones:
  - name: tomatoes
    field_capacity_mm: 40
    water_threshold_mm: 20
    crop_coefficient: 1.15
```

### Daily GitHub Action

- Added `.github/workflows/daily.yml`, scheduled for 05:17 UTC every morning and available for manual dispatch.
- The workflow updates both CSV and Delta logs, then commits and pushes the changes.
- It uses `plants.yaml` when present and otherwise falls back to `plants.example.yaml`.
- `data/watering_log.csv` is now intentionally trackable by git.

To use your local garden configuration in Actions, track `plants.yaml` or change the workflow's config path. Tracking the file in a public repository also publishes its coordinates.

### Dependencies and upgrade

The release adds `deltalake`, `pandas`, and `pyarrow`. With Python 3.10 or newer, upgrade an existing installation with:

```powershell
python -m pip install -r .\requirements.txt
```

No configuration migration is required.

### Validation

- All 8 automated tests pass, including crop-coefficient and Delta time-travel coverage.
- Two live Open-Meteo CLI runs verified CSV appends, Delta appends, and reading Delta version 0.
