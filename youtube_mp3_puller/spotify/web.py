"""Spotify web scraping and playlist page fallback helpers."""

import base64
import json
import logging
import re
from typing import Dict, List

from .utils import fetch_spotify_web_page, spotify_playlist_id_from_url
from ..exceptions import SpotifyWebError
from ..youtube.resolve import resolve_youtube_link
from spotdl.search import SongObject

logger = logging.getLogger(__name__)


def extract_spotify_web_state(html: str) -> Dict:
    script_regex = re.compile(r"<script[^>]*>(.*?)</script>", re.DOTALL | re.IGNORECASE)
    for match in script_regex.finditer(html):
        content = match.group(1).strip()
        if len(content) < 10000:
            continue
        try:
            decoded = base64.b64decode(content)
            data = json.loads(decoded)
            if isinstance(data, dict) and "entities" in data:
                return data
        except Exception:
            continue

    raise SpotifyWebError("Could not extract Spotify page JSON state")


def create_song_object_from_spotify_web_track(track_data: Dict, playlist: Dict) -> SongObject | None:
    album = track_data.get("albumOfTrack", {})
    artists_data = track_data.get("artists", {}).get("items", [])
    artists = [
        artist.get("profile", {}).get("name", "Unknown")
        for artist in artists_data
        if artist.get("profile") is not None
    ]

    album_artists_data = album.get("artists", {}).get("items", [])
    album_artists = [
        artist.get("profile", {}).get("name", "Unknown")
        for artist in album_artists_data
        if artist.get("profile") is not None
    ]

    duration_ms = int(track_data.get("duration", {}).get("totalMilliseconds", 0) or 0)
    youtube_link = resolve_youtube_link(
        track_data.get("name", "Unknown Track"),
        artists,
        album.get("name", ""),
        duration_ms,
        None,
    )

    if youtube_link is None:
        return None

    cover_art_sources = album.get("coverArt", {}).get("sources", [])
    album_images = [
        {"url": source.get("url"), "width": source.get("width"), "height": source.get("height")}
        for source in cover_art_sources
        if source.get("url")
    ]

    raw_track_meta = {
        "name": track_data.get("name", "Unknown Track"),
        "duration_ms": duration_ms,
        "track_number": track_data.get("trackNumber", 1) or 1,
        "disc_number": track_data.get("discNumber", 1) or 1,
        "album": {
            "name": album.get("name", ""),
            "artists": [{"name": name} for name in album_artists],
            "images": album_images,
            "release_date": "",
            "genres": [],
        },
        "artists": [{"name": name} for name in artists],
        "external_ids": {},
    }
    raw_artist_meta = {"name": artists[0] if artists else "Unknown", "genres": []}
    raw_album_meta = {"name": album.get("name", ""), "artists": [{"name": name} for name in album_artists], "genres": []}

    return SongObject(
        raw_track_meta=raw_track_meta,
        raw_album_meta=raw_album_meta,
        raw_artist_meta=raw_artist_meta,
        youtube_link=youtube_link,
        lyrics=None,
        playlist=playlist,
    )


def load_tracks_from_spotify_web_playlist(playlist_url: str) -> List[SongObject]:
    playlist_id = spotify_playlist_id_from_url(playlist_url)
    if playlist_id is None:
        raise SpotifyWebError("Invalid Spotify playlist URL")

    normalized_url = f"https://open.spotify.com/playlist/{playlist_id}"
    html = fetch_spotify_web_page(normalized_url)
    page_state = extract_spotify_web_state(html)

    playlist_uri = f"spotify:playlist:{playlist_id}"
    playlist_entry = page_state["entities"]["items"].get(playlist_uri)
    if playlist_entry is None:
        raise SpotifyWebError("Playlist data not found on Spotify web page")

    playlist_meta = {
        "name": playlist_entry.get("name", "Spotify Playlist"),
        "uri": playlist_uri,
    }

    tracks: List[SongObject] = []
    for item in playlist_entry.get("content", {}).get("items", []):
        track_data = item.get("itemV2", {}).get("data")
        if not track_data:
            continue

        if track_data.get("playability", {}).get("playable") is False:
            continue

        song = create_song_object_from_spotify_web_track(track_data, playlist_meta)
        if song is not None:
            tracks.append(song)
        else:
            logger.warning(
                "Could not resolve a YouTube match for track '%s'. Skipping.",
                track_data.get("name", "Unknown"),
            )

    if not tracks:
        raise SpotifyWebError("No playable tracks found in Spotify playlist page")

    return tracks
