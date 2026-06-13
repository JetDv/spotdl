"""JSON loader helpers with compatibility exports for legacy tests."""

import json
from pathlib import Path
from typing import List, Optional, Union

from spotdl.search import SongObject, from_spotify_url

from .spotify_helpers import normalize_spotify_url
from .youtube_helpers import is_youtube_url, normalize_youtube_url, normalize_song_object

__all__ = [
    "load_songs_from_json",
    "from_spotify_url",
    "normalize_spotify_url",
    "is_youtube_url",
    "normalize_youtube_url",
    "normalize_song_object",
]


def load_songs_from_json(json_path: Optional[Union[str, Path]] = None) -> List[SongObject]:
    if json_path is None:
        json_path = Path(__file__).with_name("songs.json")
    else:
        json_path = Path(json_path)

    if not json_path.is_file():
        print(f"JSON file not found: {json_path}")
        return []

    try:
        with json_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(
            f"Error: Failed to read or parse JSON file {json_path}. Ensure it exists and is valid JSON. Error: {exc}"
        )
        return []

    if not isinstance(data, dict):
        print("JSON file must contain an object mapping title->combined_url")
        return []

    songs: List[SongObject] = []
    for title, combined_url in data.items():
        try:
            youtube_url = None
            spotify_url = str(combined_url).strip()
            if "|" in spotify_url:
                parts = [part.strip() for part in spotify_url.split("|", 1)]
                youtube_url = parts[0] if is_youtube_url(parts[0]) else None
                spotify_url = parts[1] if len(parts) > 1 else spotify_url

            song = from_spotify_url(normalize_spotify_url(spotify_url))
            if youtube_url:
                song.youtube_link = normalize_youtube_url(youtube_url)
            song = normalize_song_object(song)
            songs.append(song)
            print(f"Loaded song from JSON: {title}")
        except Exception as exc:
            print(f"Error: Failed to load song '{title}': {exc}")

    return songs
