import pytest
import requests

from petrichor.notify import find_flips, send_ntfy


def _row(zone, verdict):
    return {"date": "2026-10-19", "zone": zone, "verdict": verdict}


def test_flip_from_ok_to_water():
    previous = [_row("tomatoes", "OK")]
    current = [_row("tomatoes", "WATER")]

    assert find_flips(previous, current) == ["tomatoes"]


def test_no_flip_when_staying_water():
    previous = [_row("tomatoes", "WATER")]
    current = [_row("tomatoes", "WATER")]

    assert find_flips(previous, current) == []


def test_new_zone_does_not_flip():
    assert find_flips([], [_row("tomatoes", "WATER")]) == []


def test_flip_from_skip_to_water():
    previous = [_row("tomatoes", "SKIP (rain coming)")]
    current = [_row("tomatoes", "WATER")]

    assert find_flips(previous, current) == ["tomatoes"]


def test_last_logged_verdict_wins():
    previous = [_row("tomatoes", "WATER"), _row("tomatoes", "OK")]
    current = [_row("tomatoes", "WATER")]

    assert find_flips(previous, current) == ["tomatoes"]


def test_send_ntfy_posts_to_topic(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            pass

    def fake_post(url, data, headers, timeout):
        calls.append({"url": url, "data": data, "headers": headers})
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    assert send_ntfy("my-topic", "petrichor: time to water", "tomatoes") is True
    assert calls == [
        {
            "url": "https://ntfy.sh/my-topic",
            "data": b"tomatoes",
            "headers": {"Title": "petrichor: time to water"},
        }
    ]


def test_send_ntfy_swallows_network_errors(monkeypatch, capsys):
    def failing_post(*args, **kwargs):
        raise requests.ConnectionError("no route")

    monkeypatch.setattr(requests, "post", failing_post)

    assert send_ntfy("my-topic", "title", "body") is False
    assert "Warning" in capsys.readouterr().out
