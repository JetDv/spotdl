"""Spotify URL normalization and shared helpers."""

import base64
import os
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from spotdl.search import SongObject

from ..youtube.resolve import resolve_youtube_link

import logging

logger = logging.getLogger(__name__)


def normalize_spotify_url(spotify_url: str) -> str:
    if spotify_url.startswith("spotify:"):
        return spotify_url

    try:
        parsed = urlparse(spotify_url)
    except Exception:
        return spotify_url

    if not parsed.scheme or not parsed.netloc:
        return spotify_url

    return parsed._replace(query="", fragment="").geturl()


def spotify_playlist_id_from_url(spotify_url: str) -> Optional[str]:
    if spotify_url.startswith("spotify:playlist:"):
        return spotify_url.split(":")[-1]

    try:
        parsed = urlparse(spotify_url)
    except Exception:
        return None

    if not parsed.scheme or not parsed.netloc:
        return None

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) >= 2 and path_parts[0] == "playlist":
        return path_parts[1]

    return None


def fetch_spotify_web_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def get_spotify_client_credentials_token() -> Optional[str]:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=headers,
            data=data,
            timeout=20,
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as exc:
        logger.warning("Unable to obtain Spotify client credentials bearer token: %s", exc)
        return None


def get_spotify_access_token() -> Optional[str]:
    user_token = os.environ.get("SPOTIFY_USER_TOKEN") or os.environ.get("SPOTIFY_ACCESS_TOKEN")
    if user_token:
        return user_token.strip()

    return get_spotify_client_credentials_token()


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
