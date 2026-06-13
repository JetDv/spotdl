import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from youtube_mp3_puller import downloader
from youtube_mp3_puller.types import DownloadOption


def test_get_ffmpeg_uses_system_path_when_available(monkeypatch):
    monkeypatch.setattr(downloader.shutil, "which", lambda name: "C:/ffmpeg/bin/ffmpeg.exe")
    monkeypatch.setattr(downloader.sdffmpeg, "has_correct_version", lambda exe: True)
    assert downloader.get_ffmpeg() == "C:/ffmpeg/bin/ffmpeg.exe"


def test_get_ffmpeg_falls_back_to_venv_when_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(downloader.shutil, "which", lambda name: None)
    monkeypatch.setattr(downloader.sdffmpeg, "has_correct_version", lambda exe: True)
    fake_venv = tmp_path / "Scripts"
    fake_venv.mkdir(parents=True)
    (fake_venv / "ffmpeg.exe").write_text("")
    monkeypatch.setattr(downloader.sys, "executable", str(fake_venv / "python.exe"))

    assert downloader.get_ffmpeg().endswith("ffmpeg.exe")


def test_build_song_metadata_with_raw_meta():
    song = type("Song", (), {})()
    song.song_name = None
    song._raw_track_meta = {
        "name": "Test Track",
        "duration_ms": 123456,
        "artists": [{"name": "Artist 1"}],
    }
    song._raw_album_meta = {"name": "Test Album"}

    track_name, artists, album_name, duration_ms = downloader._build_song_metadata(song)

    assert track_name == "Test Track"
    assert artists == ["Artist 1"]
    assert album_name == "Test Album"
    assert duration_ms == 123456


def test_build_song_metadata_without_raw_meta():
    song = type("Song", (), {})()

    track_name, artists, album_name, duration_ms = downloader._build_song_metadata(song)

    assert track_name == "Unknown"
    assert artists == []
    assert album_name == ""
    assert duration_ms == 0


def test_retry_failed_downloads_succeeds_on_fallback(monkeypatch):
    song = Mock()
    song.song_name = "Fallback Song"
    song._raw_track_meta = {
        "name": "Fallback Song",
        "duration_ms": 180000,
        "artists": [{"name": "Artist"}],
    }
    song._raw_album_meta = {"name": "Album"}

    manager = Mock()
    manager.download_tracker.get_song_list.side_effect = [[song], []]
    monkeypatch.setattr(downloader, "resolve_youtube_link", lambda *args, **kwargs: "https://youtu.be/fallback")
    manager.download_single_song = Mock()

    assert downloader._retry_failed_downloads(manager) is True
    manager.download_single_song.assert_called_once_with(song)


def test_retry_failed_downloads_returns_false_when_still_remaining(monkeypatch, capsys):
    song = Mock()
    manager = Mock()
    manager.download_tracker.get_song_list.side_effect = [[song], [song]]
    monkeypatch.setattr(downloader, "resolve_youtube_link", lambda *args, **kwargs: "https://youtu.be/fallback")
    manager.download_single_song = Mock()

    assert downloader._retry_failed_downloads(manager) is False


def test_perform_download_one_song(monkeypatch, tmp_path):
    manager = Mock()
    manager.download_single_song = Mock()
    manager.download_tracker.get_song_list.return_value = []

    class DummyManager:
        def __init__(self, arguments):
            self.arguments = arguments

        def __enter__(self):
            return manager

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(downloader, "DownloadManager", DummyManager)
    monkeypatch.setattr(downloader, "get_ffmpeg", lambda: "ffmpeg")

    result = downloader.perform_download(Mock(), DownloadOption.ONE_SONG, downloads_dir=tmp_path)

    assert result is True
    manager.download_single_song.assert_called_once()


def test_perform_download_multiple_songs(monkeypatch, tmp_path):
    manager = Mock()
    manager.download_multiple_songs = Mock()
    manager.download_tracker.get_song_list.return_value = []

    class DummyManager:
        def __init__(self, arguments):
            self.arguments = arguments

        def __enter__(self):
            return manager

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(downloader, "DownloadManager", DummyManager)
    monkeypatch.setattr(downloader, "get_ffmpeg", lambda: "ffmpeg")

    songs = [Mock(), Mock()]
    result = downloader.perform_download(songs, DownloadOption.PLAYLIST, downloads_dir=tmp_path)

    assert result is True
    manager.download_multiple_songs.assert_called_once_with(songs)
