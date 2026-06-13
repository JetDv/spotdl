"""Spotify API playlist fallback helpers."""

from typing import List, Optional

import requests

from .utils import get_spotify_access_token, spotify_playlist_id_from_url
from .utils import create_song_object_from_spotify_api_track
from ..exceptions import SpotifyApiError
from spotdl.search import SongObject


def load_tracks_from_spotify_api_playlist(playlist_url: str) -> List[SongObject]:
    playlist_id = spotify_playlist_id_from_url(playlist_url)
    if playlist_id is None:
        raise SpotifyApiError("Invalid Spotify playlist URL")

    token = get_spotify_access_token()
    if token is None:
        raise SpotifyApiError(
            "Spotify API /items fallback requires a user access token. Set SPOTIFY_USER_TOKEN or SPOTIFY_ACCESS_TOKEN in the environment."
        )

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": 50}
    tracks: List[SongObject] = []

    while url:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise SpotifyApiError(f"Spotify API playlist /items request failed: {exc}") from exc

        for item in data.get("items", []):
            playlist_item = item.get("item") or item.get("track")
            if not playlist_item or playlist_item.get("is_playable") is False:
                continue

            song = create_song_object_from_spotify_api_track(
                playlist_item, {"uri": f"spotify:playlist:{playlist_id}"}
            )
            if song is not None:
                tracks.append(song)

        url = data.get("next")
        params = None

    if not tracks:
        raise SpotifyApiError("No playable tracks found in Spotify playlist items.")

    return tracks
