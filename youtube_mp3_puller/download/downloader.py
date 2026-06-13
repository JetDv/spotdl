"""Download orchestration for the youtube_mp3_puller package."""

import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from spotdl.download import DownloadManager
from .ffmpeg import get_ffmpeg
from ..youtube.resolve import resolve_youtube_link
from spotdl.search import SongObject

from ..exceptions import DownloadExecutionError
from ..types import DownloadOption

logger = logging.getLogger(__name__)


def perform_download(
    choice: Union[SongObject, List[SongObject]],
    option: DownloadOption,
    ffmpeg_exe: Optional[str] = None,
    downloads_dir: Optional[Path] = None,
) -> bool:
    if ffmpeg_exe is None:
        ffmpeg_exe = get_ffmpeg()

    if downloads_dir is None:
        downloads_dir = Path(__file__).parent / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    previous_cwd = Path.cwd()
    try:
        os.chdir(downloads_dir)
        with DownloadManager(arguments={"ffmpeg": ffmpeg_exe, "download_threads": 1}) as manager:
            try:
                if option == DownloadOption.ONE_SONG:
                    manager.download_single_song(choice)
                else:
                    manager.download_multiple_songs(choice)
            except Exception as exc:
                logger.error(
                    "Download failed. Check your input and network connection. Error: %s",
                    exc,
                )
                return False

            if not _retry_failed_downloads(manager):
                return False
    finally:
        os.chdir(previous_cwd)

    logger.info("All downloads completed.")
    return True


def _build_song_metadata(song: SongObject) -> tuple[str, list[str], str, int]:
    if hasattr(song, "_raw_track_meta"):
        track_name = getattr(song, "song_name", None) or song._raw_track_meta.get("name")
    else:
        track_name = "Unknown"

    if hasattr(song, "_raw_track_meta") and song._raw_track_meta:
        artists = [
            a.get("name", "Unknown")
            for a in song._raw_track_meta.get("artists", [])
        ]
    else:
        artists = []

    album_name = ""
    if hasattr(song, "_raw_album_meta") and song._raw_album_meta:
        album_name = song._raw_album_meta.get("name", "")

    if hasattr(song, "_raw_track_meta"):
        duration_ms = getattr(song, "duration_ms", 0) or song._raw_track_meta.get("duration_ms", 0)
    else:
        duration_ms = 0

    return track_name, artists, album_name, duration_ms


def _retry_failed_downloads(manager: DownloadManager) -> bool:
    remaining_songs = manager.download_tracker.get_song_list()
    if not remaining_songs:
        return True

    logger.warning("Some tracks failed to download. Attempting fallbacks for remaining songs...")
    for song in list(remaining_songs):
        try:
            track_name, artists, album_name, duration_ms = _build_song_metadata(song)
            fallback = resolve_youtube_link(track_name, artists, album_name, duration_ms, None)
            if not fallback:
                continue
            setattr(song, "youtube_link", fallback)
            try:
                manager.download_single_song(song)
            except Exception as exc:
                logger.warning("Retry failed for %s: %s", track_name, exc)
        except Exception as exc:
            logger.warning(
                "Fallback attempt error for song %s: %s",
                getattr(song, "song_name", "unknown"),
                exc,
            )

    remaining_songs = manager.download_tracker.get_song_list()
    if remaining_songs:
        logger.warning("Some tracks still failed to download. Remaining songs: %s", remaining_songs)
        return False

    return True
