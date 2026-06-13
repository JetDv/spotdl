"""YouTube metadata discovery helpers."""

from typing import Optional

from yt_dlp import YoutubeDL

from .url import is_youtube_url, normalize_youtube_url


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
