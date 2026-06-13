from unittest.mock import Mock, patch
import pytest

from youtube_mp3_puller import youtube_helpers


def test_is_youtube_url_accepts_youtube_links():
    assert youtube_helpers.is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert youtube_helpers.is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
    assert not youtube_helpers.is_youtube_url("https://open.spotify.com/track/123")


def test_normalize_youtube_url_removes_extra_query_params():
    url = "https://www.youtube.com/watch?v=abc123&list=PL&other=1"
    normalized = youtube_helpers.normalize_youtube_url(url)
    assert "v=abc123" in normalized
    assert "list=" not in normalized


def test_youtube_has_audio_stream_returns_true_when_acodec_present(monkeypatch):
    mock_ytdl = Mock()
    mock_ytdl.extract_info.return_value = {"formats": [{"acodec": "mp4a.40.2"}]}

    monkeypatch.setattr(youtube_helpers, "YoutubeDL", lambda options: mock_ytdl)
    assert youtube_helpers.youtube_has_audio_stream("https://youtu.be/dQw4w9WgXcQ")


def test_search_youtube_query_returns_first_available_link(monkeypatch):
    entry = {"webpage_url": "https://youtu.be/example"}
    mock_ytdl = Mock()
    mock_ytdl.extract_info.return_value = {"entries": [entry]}

    monkeypatch.setattr(youtube_helpers, "YoutubeDL", lambda options: mock_ytdl)
    monkeypatch.setattr(youtube_helpers, "is_youtube_url_available", lambda url: True)

    result = youtube_helpers.search_youtube_query("Test Query", max_results=1)
    assert result == "https://youtu.be/example"


def test_create_song_object_from_youtube_url_invalid_url_raises():
    with pytest.raises(ValueError, match="Invalid YouTube URL"):
        youtube_helpers.create_song_object_from_youtube_url("https://example.com/notyoutube")


def test_resolve_youtube_link_uses_search_best_match(monkeypatch):
    monkeypatch.setattr(youtube_helpers, "search_and_get_best_match", lambda *args, **kwargs: "https://youtu.be/bestmatch")
    monkeypatch.setattr(youtube_helpers, "is_youtube_url_available", lambda url: True)

    result = youtube_helpers.resolve_youtube_link("Song", ["Artist"], "Album", 180000, None)
    assert result == "https://youtu.be/bestmatch"


def test_normalize_song_object_adds_genres_and_fallback_link(monkeypatch):
    song = Mock()
    song._raw_artist_meta = {"name": "Artist"}
    song._raw_album_meta = {"name": "Album"}
    song._raw_track_meta = {"name": "Song", "duration_ms": 180000, "artists": [{"name": "Artist"}]}
    song.youtube_link = None

    monkeypatch.setattr(youtube_helpers, "is_youtube_url_available", lambda url: False)
    monkeypatch.setattr(youtube_helpers, "resolve_youtube_link", lambda *args, **kwargs: "https://youtu.be/fallback")

    normalized = youtube_helpers.normalize_song_object(song)
    assert normalized.youtube_link == "https://youtu.be/fallback"
    assert normalized._raw_artist_meta["genres"] == []
    assert normalized._raw_album_meta["genres"] == []
