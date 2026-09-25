"""Core soil water-balance model (pure functions, no I/O).

The "bucket model": soil has a water deficit that grows with
evapotranspiration (ET0) and shrinks with precipitation. The deficit
is clamped between 0 (soil fully replenished) and field capacity
(the maximum amount of water the soil can hold for plants).
"""


def clamp(value, lo, hi):
    return max(lo, min(value, hi))


def update_deficit(prev_deficit, et0_mm, precipitation_mm, field_capacity_mm):
    """Advance the deficit by one day."""
    deficit = prev_deficit + et0_mm - precipitation_mm
    return clamp(deficit, 0.0, field_capacity_mm)


def simulate(initial_deficit, daily, field_capacity_mm):
    """Run the bucket model over a series of days.

    `daily` is an iterable of (et0_mm, precipitation_mm) tuples.
    Returns the list of end-of-day deficits.
    """
    deficits = []
    deficit = initial_deficit
    for et0_mm, precipitation_mm in daily:
        deficit = update_deficit(deficit, et0_mm, precipitation_mm, field_capacity_mm)
        deficits.append(deficit)
    return deficits


def decide(deficit, water_threshold_mm, forecast_rain_mm):
    """Return a watering verdict for a zone.

    - OK:                deficit is below the threshold, no action needed.
    - SKIP (rain coming): deficit exceeds the threshold, but the forecast
                         rain is expected to cover it — let the sky water.
    - WATER:             deficit exceeds the threshold and no rain is coming.
    """
    if deficit < water_threshold_mm:
        return "OK"
    if forecast_rain_mm >= deficit:
        return "SKIP (rain coming)"
    return "WATER"
