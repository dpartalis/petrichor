"""Load and validate the plants.yaml config."""

import yaml

REQUIRED_ZONE_KEYS = {"name", "field_capacity_mm", "water_threshold_mm"}


def load_config(path):
    """Load a plants.yaml file and return the validated config dict."""
    with open(path) as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict) or "location" not in cfg or "zones" not in cfg:
        raise ValueError("Config must contain 'location' and 'zones' sections.")

    loc = cfg["location"]
    if "latitude" not in loc or "longitude" not in loc:
        raise ValueError("'location' requires latitude and longitude.")

    if not cfg["zones"]:
        raise ValueError("'zones' must contain at least one zone.")

    for zone in cfg["zones"]:
        missing = REQUIRED_ZONE_KEYS - zone.keys()
        if missing:
            raise ValueError(
                f"Zone {zone.get('name')!r} is missing keys: {sorted(missing)}"
            )
        kc = zone.get("crop_coefficient")
        if kc is not None and (
            not isinstance(kc, (int, float)) or isinstance(kc, bool) or kc <= 0
        ):
            raise ValueError(
                f"Zone {zone.get('name')!r}: crop_coefficient must be a number > 0."
            )

    notify = cfg.get("notify")
    if notify is not None:
        if not isinstance(notify, dict) or not isinstance(
            notify.get("topic"), str
        ) or not notify["topic"].strip():
            raise ValueError("'notify' requires a non-empty 'topic' string.")

    return cfg
