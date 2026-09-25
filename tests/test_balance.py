from petrichor.balance import decide, simulate, update_deficit


def test_heavy_rain_zeroes_deficit():
    assert update_deficit(30, et0_mm=3, precipitation_mm=50, field_capacity_mm=40) == 0.0


def test_dry_week_grows_deficit():
    deficits = simulate(0.0, [(4.0, 0.0)] * 7, field_capacity_mm=40)
    assert deficits[-1] == 28.0


def test_deficit_clamped_at_field_capacity():
    assert update_deficit(39, et0_mm=5, precipitation_mm=0, field_capacity_mm=40) == 40.0


def test_skip_when_rain_covers_deficit():
    assert decide(20, water_threshold_mm=15, forecast_rain_mm=25) == "SKIP (rain coming)"


def test_water_when_dry_and_no_rain_coming():
    assert decide(20, water_threshold_mm=15, forecast_rain_mm=2) == "WATER"


def test_ok_when_below_threshold():
    assert decide(5, water_threshold_mm=15, forecast_rain_mm=0) == "OK"
