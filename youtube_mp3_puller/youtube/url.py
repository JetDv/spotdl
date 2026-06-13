"""YouTube URL parsing and normalization helpers."""

from urllib.parse import urlparse


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
