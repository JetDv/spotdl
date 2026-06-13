"""Shared type definitions for download requests and options."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DownloadOption(Enum):
    ONE_SONG = "one song"
    MULTIPLE_SONGS_JSON = "multiple songs from JSON"
    PLAYLIST = "playlist"

    @classmethod
    def labels(cls) -> List[str]:
        return [option.value for option in cls]


@dataclass
class DownloadRequest:
    option: DownloadOption
    source: Optional[str] = None
