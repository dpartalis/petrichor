from petrichor.events import append_event, apply_events, load_events


def _past():
    return [
        {"date": "2026-10-17", "et0_mm": 4.0, "precipitation_mm": 0.0},
        {"date": "2026-10-18", "et0_mm": 4.0, "precipitation_mm": 1.0},
    ]


def test_apply_events_adds_amounts_to_matching_dates():
    events = [{"date": "2026-10-17", "zone": "tomatoes", "amount_mm": "15"}]

    assert apply_events(_past(), events, "tomatoes") == [(4.0, 15.0), (4.0, 1.0)]


def test_apply_events_ignores_other_zones_and_dates():
    events = [
        {"date": "2026-10-17", "zone": "lawn", "amount_mm": "20"},
        {"date": "2026-10-10", "zone": "tomatoes", "amount_mm": "20"},
    ]

    assert apply_events(_past(), events, "tomatoes") == [(4.0, 0.0), (4.0, 1.0)]


def test_apply_events_sums_multiple_events_same_day():
    events = [
        {"date": "2026-10-18", "zone": "tomatoes", "amount_mm": "10"},
        {"date": "2026-10-18", "zone": "tomatoes", "amount_mm": "5"},
    ]

    assert apply_events(_past(), events, "tomatoes") == [(4.0, 0.0), (4.0, 16.0)]


def test_append_event_creates_file_then_appends(tmp_path):
    events_path = tmp_path / "nested" / "watering_events.csv"

    append_event(events_path, "2026-10-18", "tomatoes", 40)
    append_event(events_path, "2026-10-19", "lawn", 10)

    assert load_events(events_path) == [
        {"date": "2026-10-18", "zone": "tomatoes", "amount_mm": "40"},
        {"date": "2026-10-19", "zone": "lawn", "amount_mm": "10"},
    ]


def test_load_events_missing_file_returns_empty(tmp_path):
    assert load_events(tmp_path / "nope.csv") == []
