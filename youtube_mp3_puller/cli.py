"""Command-line prompt helpers for download requests."""

from typing import Optional

import inquirer

from .types import DownloadOption


def prompt_download_option_cli() -> Optional[DownloadOption]:
    question = [
        inquirer.List(
            "prompt",
            message="What would you like to download?",
            choices=DownloadOption.labels(),
        ),
    ]

    answer = inquirer.prompt(question)
    if not answer or "prompt" not in answer:
        return None

    try:
        return DownloadOption(answer["prompt"])
    except ValueError as exc:
        raise ValueError(f"Unknown option selected: {exc}") from exc


def prompt_song_url_cli() -> str:
    return input("Enter Spotify or YouTube song URL: ").strip()


def prompt_playlist_url_cli() -> str:
    return input("Enter Spotify playlist URL: ").strip()
