import base64
import json
from unittest.mock import Mock, patch

import pytest

from youtube_mp3_puller import spotify_helpers


def test_normalize_spotify_url_strips_query():
    normalized = spotify_helpers.normalize_spotify_url("https://open.spotify.com/track/abcd?si=xyz")
    assert normalized == "https://open.spotify.com/track/abcd"


def test_spotify_playlist_id_from_url_accepts_url_and_uri():
    assert spotify_helpers.spotify_playlist_id_from_url("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc") == "37i9dQZF1DXcBWIGoYBM5M"
    assert spotify_helpers.spotify_playlist_id_from_url("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M") == "37i9dQZF1DXcBWIGoYBM5M"


def test_spotify_playlist_id_from_url_invalid_returns_none():
    assert spotify_helpers.spotify_playlist_id_from_url("https://open.spotify.com/album/123") is None


def test_create_song_object_from_spotify_api_track_uses_youtube_fallback(monkeypatch):
    track = {
        "name": "Example Track",
        "duration_ms": 210000,
        "artists": [{"name": "Example Artist"}],
        "album": {"name": "Example Album", "artists": [{"name": "Example Artist"}], "images": []},
        "external_ids": {"isrc": "USRC17607839"},
    }
    playlist = {"uri": "spotify:playlist:123"}
    monkeypatch.setattr(spotify_helpers, "resolve_youtube_link", lambda *args, **kwargs: "https://youtu.be/fallback")

    song = spotify_helpers.create_song_object_from_spotify_api_track(track, playlist)

    assert song is not None
    assert song.youtube_link == "https://youtu.be/fallback"
    assert song._raw_track_meta["name"] == "Example Track"


def test_load_tracks_from_spotify_api_playlist_requires_token(monkeypatch):
    monkeypatch.delenv("SPOTIFY_USER_TOKEN", raising=False)
    monkeypatch.delenv("SPOTIFY_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(spotify_helpers, "get_spotify_client_credentials_token", lambda: None)

    with pytest.raises(ValueError, match="requires a user access token"):
        spotify_helpers.load_tracks_from_spotify_api_playlist("https://open.spotify.com/playlist/123")


def test_extract_spotify_web_state_from_embedded_base64():
    payload = {"entities": {"x": 1}, "padding": "A" * 12000}
    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    html = f"<html><script>{encoded}</script></html>"

    result = spotify_helpers.extract_spotify_web_state(html)
    assert result["entities"] == {"x": 1}
