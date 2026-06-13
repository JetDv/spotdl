"""Core orchestrator for the youtube_mp3_puller package.

This module exposes the public download API while delegating specific
responsibilities to dedicated helper modules.
"""

import logging
from typing import List, Union

from spotdl.search import SongObject, from_playlist, from_spotify_url

from .cli import (
    prompt_download_option_cli,
    prompt_playlist_url_cli,
    prompt_song_url_cli,
)
from .downloader import perform_download
from .env_utils import init_spotdl_client
from .loaders.json_loader import load_songs_from_json
from .spotify.api import load_tracks_from_spotify_api_playlist
from .spotify.web import load_tracks_from_spotify_web_playlist
from .spotify.utils import normalize_spotify_url
from .types import DownloadOption, DownloadRequest
from .youtube.resolve import create_song_object_from_youtube_url, normalize_song_object
from .youtube.url import is_youtube_url
from .exceptions import DownloadRequestError, SpotifyApiError, SpotifyWebError
from . import spotify_helpers
from . import youtube_helpers

logger = logging.getLogger(__name__)

# Compatibility exports for legacy callers and tests.
normalize_youtube_url = youtube_helpers.normalize_youtube_url
spotify_playlist_id_from_url = spotify_helpers.spotify_playlist_id_from_url


def _prepare_one_song(source: str) -> SongObject:
    if not source:
        raise DownloadRequestError("Song URL is required for one song downloads.")

    source = source.strip()
    if is_youtube_url(source):
        return normalize_song_object(create_song_object_from_youtube_url(source))

    normalized_source = normalize_spotify_url(source)
    try:
        song = from_spotify_url(normalized_source)
    except Exception as exc:
        raise SpotifyApiError(
            f"Spotify track resolution failed for {normalized_source}"
        ) from exc

    return normalize_song_object(song)


def _prepare_playlist(source: str) -> List[SongObject]:
    if not source:
        raise DownloadRequestError("Playlist URL is required for playlist downloads.")

    normalized_source = normalize_spotify_url(source.strip())

    try:
        songs = from_playlist(normalized_source)
        return [normalize_song_object(song) for song in songs]
    except Exception as exc:
        logger.warning(
            "Spotify API failed for playlist URL. Trying direct /items fallback. Error: %s",
            exc,
        )

    try:
        songs = load_tracks_from_spotify_api_playlist(normalized_source)
        return [normalize_song_object(song) for song in songs]
    except Exception as exc:
        logger.warning(
            "Spotify /items fallback failed. Falling back to web scraping. Error: %s",
            exc,
        )

    try:
        songs = load_tracks_from_spotify_web_playlist(normalized_source)
        return [normalize_song_object(song) for song in songs]
    except Exception as exc:
        raise SpotifyWebError(
            f"Playlist resolution failed for {normalized_source}"
        ) from exc


def _prepare_from_json(source: str) -> List[SongObject]:
    if not source:
        raise DownloadRequestError("JSON file path is required for multiple songs downloads.")
    return load_songs_from_json(source)


def prepare_download_choice(request: DownloadRequest) -> Union[SongObject, List[SongObject]]:
    if request.option == DownloadOption.ONE_SONG:
        return _prepare_one_song(request.source or "")

    if request.option == DownloadOption.PLAYLIST:
        return _prepare_playlist(request.source or "")

    if request.option == DownloadOption.MULTIPLE_SONGS_JSON:
        return _prepare_from_json(request.source or "")

    raise DownloadRequestError(f"Unsupported download option: {request.option}")


def download(request: DownloadRequest) -> bool:
    choice = prepare_download_choice(request)
    return perform_download(choice, request.option)


def main() -> None:
    init_spotdl_client()

    try:
        option = prompt_download_option_cli()
        if option is None:
            logger.info("No download option selected.")
            return

        source = None
        if option == DownloadOption.ONE_SONG:
            source = prompt_song_url_cli()
        elif option == DownloadOption.PLAYLIST:
            source = prompt_playlist_url_cli()

        request = DownloadRequest(option=option, source=source)
        download(request)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
    except Exception as exc:
        logger.error("Error: %s", exc)
