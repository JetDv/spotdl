"""Unit tests for core helper functions in the spotdl downloader package."""
# pylint: disable=duplicate-code

from youtube_mp3_puller import core


def test_is_youtube_url():
    assert core.is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert core.is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
    assert not core.is_youtube_url("https://open.spotify.com/track/123")


def test_normalize_youtube_url():
    url = "https://www.youtube.com/watch?v=abc123&list=PL&other=1"
    normalized = core.normalize_youtube_url(url)
    assert "v=abc123" in normalized
    assert "list=" not in normalized


def test_normalize_spotify_url():
    url = "https://open.spotify.com/track/abcd?si=xyz"
    normalized = core.normalize_spotify_url(url)
    assert "?" not in normalized


def test_spotify_playlist_id_from_url():
    url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc"
    pid = core.spotify_playlist_id_from_url(url)
    assert pid == "37i9dQZF1DXcBWIGoYBM5M"
