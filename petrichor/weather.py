"""Fetch past + forecast weather from Open-Meteo (free, no API key)."""

import requests

API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_daily(latitude, longitude, past_days=7, forecast_days=7, timezone="auto"):
    """Return a list of daily records: date, precipitation (mm), ET0 (mm).

    The list covers `past_days` of observed data through `forecast_days`
    of forecast, in chronological order.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum,et0_fao_evapotranspiration",
        "past_days": past_days,
        "forecast_days": forecast_days,
        "timezone": timezone,
    }
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    daily = resp.json()["daily"]

    return [
        {
            "date": d,
            "precipitation_mm": p if p is not None else 0.0,
            "et0_mm": e if e is not None else 0.0,
        }
        for d, p, e in zip(
            daily["time"],
            daily["precipitation_sum"],
            daily["et0_fao_evapotranspiration"],
        )
    ]


def split_past_forecast(days, today):
    """Split daily records into observed (before today) and forecast."""
    past = [d for d in days if d["date"] < today]
    forecast = [d for d in days if d["date"] >= today]
    return past, forecast
