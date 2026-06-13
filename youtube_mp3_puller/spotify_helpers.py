"""Legacy Spotify helper compatibility wrappers.

This module delegates the implementation to the modern
`youtube_mp3_puller.spotify` subpackage while preserving the legacy
public API and exception behavior used by existing callers and tests.
"""

from typing import Dict, List, Optional

from spotdl.search import SongObject

from .spotify.api import load_tracks_from_spotify_api_playlist as _load_tracks_from_spotify_api_playlist
from .spotify.utils import (
    fetch_spotify_web_page,
    get_spotify_access_token,
    get_spotify_client_credentials_token,
    normalize_spotify_url,
    spotify_playlist_id_from_url,
)
from .spotify.web import (
    create_song_object_from_spotify_web_track,
    extract_spotify_web_state as _extract_spotify_web_state,
    load_tracks_from_spotify_web_playlist as _load_tracks_from_spotify_web_playlist,
)
from .youtube_helpers import resolve_youtube_link
from .exceptions import SpotifyApiError, SpotifyWebError

__all__ = [
    "normalize_spotify_url",
    "spotify_playlist_id_from_url",
    "fetch_spotify_web_page",
    "get_spotify_client_credentials_token",
    "get_spotify_access_token",
    "create_song_object_from_spotify_api_track",
    "load_tracks_from_spotify_api_playlist",
    "extract_spotify_web_state",
    "create_song_object_from_spotify_web_track",
    "load_tracks_from_spotify_web_playlist",
]


def create_song_object_from_spotify_api_track(track: Dict, playlist: Dict) -> Optional[SongObject]:
    if not track:
        return None

    artist_names = [
        artist.get("name", "Unknown")
        for artist in track.get("artists", [])
        if artist.get("name")
    ]
    album = track.get("album", {})
    album_artists = [
        {"name": artist.get("name", "Unknown")}
        for artist in album.get("artists", [])
        if artist.get("name")
    ]
    album_images = [
        {
            "url": image.get("url"),
            "width": image.get("width"),
            "height": image.get("height"),
        }
        for image in album.get("images", [])
        if image.get("url")
    ]
    duration_ms = int(track.get("duration_ms") or 0)
    isrc = track.get("external_ids", {}).get("isrc")

    youtube_link = resolve_youtube_link(
        track.get("name", "Unknown Track"),
        artist_names,
        album.get("name", ""),
        duration_ms,
        isrc,
    )

    if youtube_link is None:
        return None

    raw_track_meta = {
        "name": track.get("name", "Unknown Track"),
        "duration_ms": duration_ms,
        "track_number": track.get("track_number", 1) or 1,
        "disc_number": track.get("disc_number", 1) or 1,
        "album": {
            "name": album.get("name", ""),
            "artists": album_artists,
            "images": album_images,
            "release_date": album.get("release_date", ""),
            "genres": [],
        },
        "artists": [{"name": name} for name in artist_names],
        "external_ids": track.get("external_ids", {}),
    }
    raw_artist_meta = {"name": artist_names[0] if artist_names else "Unknown", "genres": []}
    raw_album_meta = {"name": album.get("name", ""), "artists": album_artists, "genres": []}

    return SongObject(
        raw_track_meta=raw_track_meta,
        raw_album_meta=raw_album_meta,
        raw_artist_meta=raw_artist_meta,
        youtube_link=youtube_link,
        lyrics=None,
        playlist=playlist,
    )


def load_tracks_from_spotify_api_playlist(playlist_url: str) -> List["SongObject"]:
    try:
        return _load_tracks_from_spotify_api_playlist(playlist_url)
    except SpotifyApiError as exc:
        raise ValueError(str(exc)) from exc


def extract_spotify_web_state(html: str) -> Dict:
    try:
        return _extract_spotify_web_state(html)
    except SpotifyWebError as exc:
        raise ValueError(str(exc)) from exc


def load_tracks_from_spotify_web_playlist(playlist_url: str) -> List["SongObject"]:
    try:
        return _load_tracks_from_spotify_web_playlist(playlist_url)
    except SpotifyWebError as exc:
        raise ValueError(str(exc)) from exc
