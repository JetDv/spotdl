"""Load song metadata definitions from JSON files."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Union

from spotdl.search import SongObject, from_spotify_url

from ..exceptions import JsonLoadError
from ..spotify.utils import normalize_spotify_url
from ..youtube.url import is_youtube_url
from ..youtube.resolve import normalize_youtube_url, normalize_song_object

logger = logging.getLogger(__name__)


def load_songs_from_json(json_path: Optional[Union[str, Path]] = None) -> List[SongObject]:
    if json_path is None:
        json_path = Path(__file__).with_name("songs.json")
    else:
        json_path = Path(json_path)

    if not json_path.is_file():
        raise JsonLoadError(f"JSON file not found: {json_path}")

    try:
        with json_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise JsonLoadError(
            f"Failed to read or parse JSON file {json_path}. Ensure it exists and is valid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise JsonLoadError("JSON file must contain an object mapping title->combined_url")

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
            logger.info("Loaded song from JSON: %s", title)
        except Exception as exc:
            logger.warning("Failed to load song '%s': %s", title, exc)

    return songs
