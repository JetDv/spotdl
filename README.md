# SpotDL YouTube MP3 Puller

This project wraps the `spotdl` package to download songs from Spotify and YouTube.
It now uses a refactored internal package structure with a stable package entrypoint for compatibility.

Features:
- Package entrypoint via `python -m youtube_mp3_puller`.
- Refactored core logic in `youtube_mp3_puller/` with dedicated helper modules.
- Optional GUI frontend in `youtube_mp3_puller_ui.py` using Tkinter.
- JSON-based song loading and playlist fallback support.
- `pylint`-clean with the provided `.pylintrc`.

Project structure:
- `youtube_mp3_puller/__main__.py` — package entrypoint for `python -m youtube_mp3_puller`.
- `youtube_mp3_puller/__init__.py` — stable package API surface.
- `youtube_mp3_puller/core.py` — orchestrates downloads and fallback strategies.
- `youtube_mp3_puller/env_utils.py` — loads `.env` and configures Spotify credentials.
- `youtube_mp3_puller/spotify/` — Spotify helpers, API fallback, and web scraping.
- `youtube_mp3_puller/youtube/` — YouTube URL parsing, search, and resolution.
- `youtube_mp3_puller/loaders/json_loader.py` — loads song definitions from JSON.
- `youtube_mp3_puller/download/` — download orchestration and FFmpeg support.
- `youtube_mp3_puller/cli.py` — CLI prompts for interactive usage.
- `youtube_mp3_puller/types.py` — shared request and option types.

Usage
-----
1. Create a `.env` file in the project root or set environment variables:

```text
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

2. Run using the project virtual environment:

```powershell
cd C:\dev\Python\spotdl
.\venv\Scripts\Activate.ps1
python -m youtube_mp3_puller
```

3. Run the GUI:

```powershell
python youtube_mp3_puller_ui.py
```

Design Patterns
---------------
- **Facade:** `youtube_mp3_puller.__init__.py` provides a stable public API while hiding implementation details.
- **Single Responsibility:** Each module has a focused responsibility: environment loading, Spotify resolution, YouTube resolution, JSON parsing, download orchestration, or CLI prompts.
- **Adapter:** The package adapts upstream `spotdl` and `yt-dlp` interfaces into a consistent internal download flow.
- **Strategy:** Playlist downloads attempt multiple resolution strategies: native SpotDL playlist handling, Spotify API fallback, and web page scraping.

Notes
-----
- The code loads `.env` values only when they are missing from the environment.
- FFmpeg is required and is located automatically from the venv or PATH.
- Compatibility is preserved by keeping `DownloadOption`, `DownloadRequest`, `download`, `init_spotdl_client`, and `main` available at the top level.
- Do not store `.venv` or any generated virtual environment files in the repository. Use `requirements.txt` and the provided `setup_venv.bat` helper to recreate the environment.
