"""youtube_mp3_puller package facade.

This package provides the stable public API for the downloader while hiding
implementation details in smaller submodules and helper packages.
"""
from .core import (
    DownloadOption,
    DownloadRequest,
    download,
    init_spotdl_client,
    prepare_download_choice,
    perform_download,
    main,
)
from .exceptions import (
    DownloadRequestError,
    SpotifyApiError,
    SpotifyWebError,
    YoutubeResolutionError,
    DownloadExecutionError,
    JsonLoadError,
    SpotifyClientInitializationError,
)

__all__ = [
    "DownloadOption",
    "DownloadRequest",
    "download",
    "init_spotdl_client",
    "prepare_download_choice",
    "perform_download",
    "main",
    "DownloadRequestError",
    "SpotifyApiError",
    "SpotifyWebError",
    "YoutubeResolutionError",
    "DownloadExecutionError",
    "JsonLoadError",
    "SpotifyClientInitializationError",
]
