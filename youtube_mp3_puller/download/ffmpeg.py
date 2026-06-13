"""FFmpeg discovery helpers for downloads."""

import logging
import shutil
import sys
from pathlib import Path

from spotdl.download import ffmpeg as sdffmpeg

logger = logging.getLogger(__name__)


def get_ffmpeg() -> str:
    ffmpeg_exe = shutil.which("ffmpeg")
    if not ffmpeg_exe:
        venv_scripts = Path(sys.executable).parent
        candidate = venv_scripts / "ffmpeg.exe"
        if candidate.exists():
            ffmpeg_exe = str(candidate)
        else:
            ffmpeg_exe = "ffmpeg"

    try:
        sdffmpeg.has_correct_version(ffmpeg_exe)
    except Exception as exc:
        logger.debug("FFmpeg version check failed for %s: %s", ffmpeg_exe, exc)
    return ffmpeg_exe
