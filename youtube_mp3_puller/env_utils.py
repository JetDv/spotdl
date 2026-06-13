"""Environment loading helpers for Spotify configuration."""

import logging
import os
from pathlib import Path

from spotdl import search

logger = logging.getLogger(__name__)


def load_dotenv_file() -> None:
    candidates = [
        Path(__file__).with_name(".env"),
        Path(__file__).resolve().parent.parent / ".env",
    ]

    for env_path in candidates:
        if not env_path.is_file():
            continue
        try:
            with env_path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as exc:
            logger.debug("Skipping unreadable env file %s: %s", env_path, exc)
            continue

    if "SPOTIPY_CLIENT_ID" not in os.environ and "SPOTIFY_CLIENT_ID" in os.environ:
        os.environ["SPOTIPY_CLIENT_ID"] = os.environ["SPOTIFY_CLIENT_ID"]
    if "SPOTIPY_CLIENT_SECRET" not in os.environ and "SPOTIFY_CLIENT_SECRET" in os.environ:
        os.environ["SPOTIPY_CLIENT_SECRET"] = os.environ["SPOTIFY_CLIENT_SECRET"]


def init_spotdl_client() -> None:
    load_dotenv_file()
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    try:
        search.SpotifyClient.init(client_id, client_secret, False)
    except (ValueError, TypeError) as exc:
        logger.warning(
            "Failed to initialize Spotify client. Please check your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in the .env file. Error: %s",
            exc,
        )
