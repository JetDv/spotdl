import builtins
from pathlib import Path
from unittest.mock import Mock

import pytest

import youtube_mp3_puller_ui
import youtube_mp3_puller._ui as ui_module
from youtube_mp3_puller import cli
from youtube_mp3_puller.types import DownloadOption, DownloadRequest


def make_ui_app(monkeypatch):
    monkeypatch.setattr(ui_module, "init_spotdl_client", lambda: None)
    app = youtube_mp3_puller_ui.SpotdlDownloaderUI()
    app.withdraw()
    return app


def test_browse_json_file_sets_selection_and_status(monkeypatch, tmp_path):
    app = make_ui_app(monkeypatch)
    filename = tmp_path / "songs.json"
    filename.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        ui_module.filedialog,
        "askopenfilename",
        lambda **kwargs: str(filename),
    )
    monkeypatch.setattr(app, "after", lambda delay, callback=None: callback() if callback else None)

    app.browse_json_file()

    assert app._state["file_path_var"].get().endswith("songs.json")
    assert "Selected JSON file" in app._state["status_var"].get()


def test_on_download_with_empty_song_source_sets_error(monkeypatch):
    app = make_ui_app(monkeypatch)
    app._state["option_var"].set(DownloadOption.ONE_SONG.value)
    app._state["source_var"].set("")
    monkeypatch.setattr(app, "after", lambda delay, callback=None: callback() if callback else None)

    app.on_download()

    assert "Please enter a Spotify URL" in app._state["status_var"].get()


def test_on_download_with_empty_json_source_sets_error(monkeypatch):
    app = make_ui_app(monkeypatch)
    app._state["option_var"].set(DownloadOption.MULTIPLE_SONGS_JSON.value)
    app._state["file_path_var"].set("")
    monkeypatch.setattr(app, "after", lambda delay, callback=None: callback() if callback else None)

    app.on_download()

    assert "Please select a JSON file" in app._state["status_var"].get()


def test_download_in_background_success_sets_success_state(monkeypatch):
    app = make_ui_app(monkeypatch)
    app._widgets["download_button"].config = Mock()
    monkeypatch.setattr(ui_module, "download", lambda request: True)
    monkeypatch.setattr(app, "after", lambda delay, callback=None: callback() if callback else None)

    app.download_in_background(DownloadRequest(option=DownloadOption.ONE_SONG, source="https://youtu.be/dQw4w9WgXcQ"))

    assert app._state["status_var"].get() == "Download finished successfully."
    app._widgets["download_button"].config.assert_called_once_with(state="normal")


def test_download_in_background_failure_sets_error_state(monkeypatch):
    app = make_ui_app(monkeypatch)
    app._widgets["download_button"].config = Mock()
    monkeypatch.setattr(ui_module, "download", lambda request: False)
    monkeypatch.setattr(app, "after", lambda delay, callback=None: callback() if callback else None)

    app.download_in_background(DownloadRequest(option=DownloadOption.ONE_SONG, source="https://youtu.be/dQw4w9WgXcQ"))

    assert "Download failed" in app._state["status_var"].get()
    app._widgets["download_button"].config.assert_called_once_with(state="normal")


def test_prompt_download_option_cli_returns_option(monkeypatch):
    monkeypatch.setattr(cli.inquirer, "prompt", lambda question: {"prompt": DownloadOption.ONE_SONG.value})

    result = cli.prompt_download_option_cli()

    assert result == DownloadOption.ONE_SONG


def test_prompt_download_option_cli_returns_none_when_cancelled(monkeypatch):
    monkeypatch.setattr(cli.inquirer, "prompt", lambda question: None)

    assert cli.prompt_download_option_cli() is None


def test_prompt_download_option_cli_raises_for_invalid_choice(monkeypatch):
    monkeypatch.setattr(cli.inquirer, "prompt", lambda question: {"prompt": "invalid option"})

    with pytest.raises(ValueError, match="Unknown option selected"):
        cli.prompt_download_option_cli()


def test_prompt_song_url_cli_strips_input(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda prompt="": "  https://youtu.be/dQw4w9WgXcQ  ")

    assert cli.prompt_song_url_cli() == "https://youtu.be/dQw4w9WgXcQ"


def test_prompt_playlist_url_cli_strips_input(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda prompt="": "  https://open.spotify.com/playlist/123  ")

    assert cli.prompt_playlist_url_cli() == "https://open.spotify.com/playlist/123"
