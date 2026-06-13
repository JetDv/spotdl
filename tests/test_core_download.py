import pytest
from unittest.mock import Mock

from youtube_mp3_puller import core
from youtube_mp3_puller.types import DownloadOption, DownloadRequest


def test_prepare_download_choice_one_song_youtube(monkeypatch):
    request = DownloadRequest(option=DownloadOption.ONE_SONG, source="https://youtu.be/dQw4w9WgXcQ")
    expected_song = Mock()
    monkeypatch.setattr(core, "is_youtube_url", lambda url: True)
    monkeypatch.setattr(core, "create_song_object_from_youtube_url", lambda url: expected_song)
    monkeypatch.setattr(core, "normalize_song_object", lambda song: song)

    result = core.prepare_download_choice(request)

    assert result is expected_song


def test_prepare_download_choice_one_song_spotify(monkeypatch):
    request = DownloadRequest(option=DownloadOption.ONE_SONG, source="https://open.spotify.com/track/abc123")
    expected_song = Mock()
    monkeypatch.setattr(core, "is_youtube_url", lambda url: False)
    monkeypatch.setattr(core, "normalize_spotify_url", lambda url: url)
    monkeypatch.setattr(core, "from_spotify_url", lambda url: expected_song)
    monkeypatch.setattr(core, "normalize_song_object", lambda song: song)

    result = core.prepare_download_choice(request)

    assert result is expected_song


def test_prepare_download_choice_playlist_fallback_to_items(monkeypatch):
    request = DownloadRequest(option=DownloadOption.PLAYLIST, source="https://open.spotify.com/playlist/playlistid")
    song1 = Mock()
    monkeypatch.setattr(core, "normalize_spotify_url", lambda url: url)
    monkeypatch.setattr(core, "from_playlist", lambda url: (_ for _ in ()).throw(Exception("API failure")))
    monkeypatch.setattr(core, "load_tracks_from_spotify_api_playlist", lambda url: [song1])
    monkeypatch.setattr(core, "normalize_song_object", lambda song: song)

    result = core.prepare_download_choice(request)

    assert result == [song1]


def test_prepare_download_choice_playlist_fallback_to_web(monkeypatch):
    request = DownloadRequest(option=DownloadOption.PLAYLIST, source="https://open.spotify.com/playlist/playlistid")
    song1 = Mock()
    monkeypatch.setattr(core, "normalize_spotify_url", lambda url: url)
    monkeypatch.setattr(core, "from_playlist", lambda url: (_ for _ in ()).throw(Exception("API failure")))
    monkeypatch.setattr(core, "load_tracks_from_spotify_api_playlist", lambda url: (_ for _ in ()).throw(Exception("items failure")))
    monkeypatch.setattr(core, "load_tracks_from_spotify_web_playlist", lambda url: [song1])
    monkeypatch.setattr(core, "normalize_song_object", lambda song: song)

    result = core.prepare_download_choice(request)

    assert result == [song1]


def test_prepare_download_choice_missing_source_errors():
    with pytest.raises(ValueError, match="Song URL is required"):
        core.prepare_download_choice(DownloadRequest(option=DownloadOption.ONE_SONG, source=None))

    with pytest.raises(ValueError, match="Playlist URL is required"):
        core.prepare_download_choice(DownloadRequest(option=DownloadOption.PLAYLIST, source=""))

    with pytest.raises(ValueError, match="JSON file path is required"):
        core.prepare_download_choice(DownloadRequest(option=DownloadOption.MULTIPLE_SONGS_JSON, source=None))


def test_download_forwards_to_perform_download(monkeypatch):
    request = DownloadRequest(option=DownloadOption.ONE_SONG, source="https://youtu.be/dQw4w9WgXcQ")
    expected_choice = Mock()
    monkeypatch.setattr(core, "prepare_download_choice", lambda req: expected_choice)
    monkeypatch.setattr(core, "perform_download", lambda choice, option: True)

    assert core.download(request) is True
