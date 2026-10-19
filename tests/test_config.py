import pytest
import yaml

from petrichor.config import load_config


def _write_config(tmp_path, **overrides):
    cfg = {
        "location": {"latitude": 38.36, "longitude": 26.13},
        "zones": [
            {
                "name": "tomatoes",
                "field_capacity_mm": 40,
                "water_threshold_mm": 20,
            }
        ],
    }
    cfg.update(overrides)
    path = tmp_path / "plants.yaml"
    path.write_text(yaml.safe_dump(cfg))
    return path


def test_valid_minimal_config(tmp_path):
    cfg = load_config(_write_config(tmp_path))

    assert cfg["zones"][0]["name"] == "tomatoes"


def test_missing_zone_keys_rejected(tmp_path):
    path = _write_config(tmp_path, zones=[{"name": "tomatoes"}])

    with pytest.raises(ValueError, match="missing keys"):
        load_config(path)


def test_bad_crop_coefficient_rejected(tmp_path):
    bad = _write_config(tmp_path)
    cfg = yaml.safe_load(bad.read_text())
    cfg["zones"][0]["crop_coefficient"] = -1
    bad.write_text(yaml.safe_dump(cfg))

    with pytest.raises(ValueError, match="crop_coefficient"):
        load_config(bad)


def test_notify_requires_topic(tmp_path):
    path = _write_config(tmp_path, notify={"topic": "  "})

    with pytest.raises(ValueError, match="notify"):
        load_config(path)


def test_notify_valid(tmp_path):
    cfg = load_config(_write_config(tmp_path, notify={"topic": "my-garden-x7q"}))

    assert cfg["notify"]["topic"] == "my-garden-x7q"
