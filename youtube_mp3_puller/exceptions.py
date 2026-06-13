"""Domain-specific exceptions for the youtube_mp3_puller package."""

class DownloadRequestError(ValueError):
    """Raised when a download request is invalid or incomplete."""


class SpotifyApiError(Exception):
    """Raised for Spotify API or Spotify URL resolution failures."""


class SpotifyWebError(Exception):
    """Raised for Spotify web scraping and playlist fallback failures."""


class YoutubeResolutionError(Exception):
    """Raised when YouTube metadata or resolution fails."""


class DownloadExecutionError(Exception):
    """Raised when a download execution failure occurs."""


class JsonLoadError(Exception):
    """Raised when JSON loading or validation fails."""


class SpotifyClientInitializationError(Exception):
    """Raised when Spotify client initialization fails."""
