import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from youtube_mp3_puller import json_loader


def test_load_songs_from_json_returns_empty_for_missing_file():
    result = json_loader.load_songs_from_json("nonexistent-file.json")
    assert result == []


def test_load_songs_from_json_parses_valid_file_with_youtube_override(monkeypatch):
    song = Mock()
    song.youtube_link = None
    monkeypatch.setattr(json_loader, "from_spotify_url", lambda url: song)
    monkeypatch.setattr(json_loader, "normalize_spotify_url", lambda url: url)
    monkeypatch.setattr(json_loader, "is_youtube_url", lambda url: True)
    monkeypatch.setattr(json_loader, "normalize_youtube_url", lambda url: url)
    monkeypatch.setattr(json_loader, "normalize_song_object", lambda s: s)

    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "songs.json"
        file_path.write_text(json.dumps({"Example": "https://youtu.be/example | https://open.spotify.com/track/abc"}), encoding="utf-8")

        result = json_loader.load_songs_from_json(file_path)

    assert len(result) == 1
    assert result[0] is song
    assert song.youtube_link == "https://youtu.be/example"
