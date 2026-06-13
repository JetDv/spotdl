"""YouTube URL and song object helpers for the downloader package."""

from typing import List, Optional
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from spotdl.providers.ytm_provider import search_and_get_best_match
from spotdl.search import SongObject


def is_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if not parsed.scheme or not parsed.netloc:
        return False

    hostname = parsed.netloc.lower()
    return hostname.endswith("youtube.com") or hostname.endswith("youtu.be")


def normalize_youtube_url(youtube_url: str) -> str:
    parsed = urlparse(youtube_url)
    if parsed.netloc.lower().endswith("youtu.be"):
        return youtube_url

    keep_params = [part for part in parsed.query.split("&") if part.startswith("v=")]
    return parsed._replace(query="&".join(keep_params)).geturl()


def youtube_has_audio_stream(youtube_url: str) -> bool:
    normalized_url = normalize_youtube_url(youtube_url)
    candidate_options = [
        {"quiet": True, "no_warnings": True, "noplaylist": True, "nocheckcertificate": True},
        {"quiet": True, "no_warnings": True, "noplaylist": True, "geo_bypass": True, "nocheckcertificate": True},
    ]

    for options in candidate_options:
        try:
            ytdl = YoutubeDL(options)
            info = ytdl.extract_info(normalized_url, download=False)
            if not info:
                continue
            formats = info.get("formats") or []
            for fmt in formats:
                acodec = fmt.get("acodec")
                if acodec and acodec.lower() != "none":
                    return True
            top_acodec = info.get("acodec")
            if top_acodec and top_acodec.lower() != "none":
                return True
        except Exception:
            continue

    return False


def is_youtube_url_available(youtube_url: str) -> bool:
    if not youtube_url:
        return False
    return youtube_has_audio_stream(youtube_url)


def search_youtube_query(query: str, max_results: int = 6) -> Optional[str]:
    ytdl = YoutubeDL(
        {
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "noplaylist": True,
        }
    )

    try:
        info = ytdl.extract_info(f"ytsearch{max_results}:{query}", download=False)
    except Exception:
        return None

    if not info:
        return None

    for entry in info.get("entries", []) or []:
        if not entry:
            continue
        youtube_link = entry.get("webpage_url") or entry.get("url")
        if youtube_link and is_youtube_url_available(youtube_link):
            return youtube_link

    return None


def create_song_object_from_youtube_url(youtube_url: str) -> SongObject:
    if not is_youtube_url(youtube_url):
        raise ValueError("Invalid YouTube URL")

    normalized_url = normalize_youtube_url(youtube_url)
    extract_options = [
        {"quiet": True, "no_warnings": True, "noplaylist": True},
        {"quiet": True, "no_warnings": True, "noplaylist": True, "geo_bypass": True},
    ]

    info = None
    last_error: Optional[Exception] = None
    for opts in extract_options:
        ytdl = YoutubeDL(opts)
        try:
            info = ytdl.extract_info(normalized_url, download=False)
            break
        except DownloadError as exc:
            last_error = exc
        except Exception as exc:
            last_error = exc

    if info is None:
        error_message = (
            "Unable to inspect YouTube video. This may mean the video is unavailable or restricted."
        )
        if last_error:
            error_message += f" Cause: {last_error}"
        raise ValueError(error_message)

    title = info.get("title", "YouTube Track")
    duration = info.get("duration") or 0
    uploader = info.get("uploader") or "YouTube"

    raw_track_meta = {
        "name": title,
        "duration_ms": int(duration * 1000),
        "track_number": 1,
        "disc_number": 1,
        "album": {
            "name": title,
            "artists": [{"name": uploader}],
            "images": [],
            "release_date": "",
            "genres": [],
        },
        "artists": [{"name": uploader}],
        "external_ids": {},
    }

    raw_artist_meta = {"name": uploader, "genres": []}
    raw_album_meta = {"name": title, "artists": [{"name": uploader}], "genres": []}

    return SongObject(
        raw_track_meta=raw_track_meta,
        raw_album_meta=raw_album_meta,
        raw_artist_meta=raw_artist_meta,
        youtube_link=normalized_url,
        lyrics=None,
        playlist=None,
    )


def resolve_youtube_link(
    track_name: str,
    artists: List[str],
    album_name: str,
    duration_ms: int,
    isrc: Optional[str],
) -> Optional[str]:
    spotify_duration = duration_ms or 1
    youtube_link = search_and_get_best_match(
        track_name,
        artists,
        album_name,
        spotify_duration,
        isrc,
    )

    if youtube_link and is_youtube_url_available(youtube_link):
        return youtube_link

    query_pieces = [track_name]
    if artists:
        query_pieces.append(" ".join(artists[:2]))
    if album_name:
        query_pieces.append(album_name)
    fallback_query = " ".join(piece.strip() for piece in query_pieces if piece)

    fallback_link = search_youtube_query(fallback_query)
    if fallback_link:
        return fallback_link

    if artists:
        artist_query = f"{track_name} {artists[0]}"
        fallback_link = search_youtube_query(artist_query)
        if fallback_link:
            return fallback_link

    return None


def normalize_song_object(song: SongObject) -> SongObject:
    if song is None:
        return song

    if hasattr(song, "_raw_artist_meta") and song._raw_artist_meta:
        song._raw_artist_meta.setdefault("genres", [])

    if hasattr(song, "_raw_album_meta") and song._raw_album_meta:
        song._raw_album_meta.setdefault("genres", [])

    if not hasattr(song, "_raw_track_meta") or not song._raw_track_meta:
        return song

    track_name = song._raw_track_meta.get("name", "Unknown")
    artists = [
        artist.get("name", "Unknown")
        for artist in song._raw_track_meta.get("artists", [])
    ]
    album_name = song._raw_album_meta.get("name", "") if hasattr(song, "_raw_album_meta") and song._raw_album_meta else ""
    duration_ms = song._raw_track_meta.get("duration_ms", 0)

    youtube_link = getattr(song, "youtube_link", None)
    if not youtube_link or not is_youtube_url_available(youtube_link):
        fallback_link = resolve_youtube_link(track_name, artists, album_name, duration_ms, None)
        if fallback_link:
            song.youtube_link = fallback_link

    return song
