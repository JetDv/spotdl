# spotdl Project Setup & Usage Guide

## Overview
This project wraps the `spotdl` package to download songs from Spotify, YouTube, playlists, and JSON-defined song lists.
The implementation is now split into a dedicated internal package with a lightweight top-level facade and GUI frontend.

**Project Root:** `C:\dev\Python\spotdl`

---

## Environment Setup

### Virtual Environment
A Python 3.14 virtual environment exists at:
```
C:\dev\Python\spotdl\.venv
```

### Dependencies
Installed packages include:
- `spotdl`
- `spotipy`
- `yt-dlp`

The project uses the venv Python interpreter for execution.

### FFmpeg
FFmpeg is expected to be available in the venv `Scripts` folder or on PATH. The code locates FFmpeg automatically and validates it through `spotdl.download.ffmpeg`.

---

## Entry Points

### `python -m youtube_mp3_puller`

**Entry point:** `youtube_mp3_puller/__main__.py`

This package entrypoint runs the internal downloader through the package API surface:
- `DownloadOption`
- `DownloadRequest`
- `download`
- `init_spotdl_client`
- `main`

It provides a stable public API while delegating implementation details to `youtube_mp3_puller`.

### `youtube_mp3_puller_ui.py`

This file provides a Tkinter-based graphical frontend that calls the same backend entry points.

---

## Configuration Files

### `.env` (optional)
Create `C:\dev\Python\spotdl\.env` with:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

The code loads `.env` from the project root and maps these values to the `SPOTIPY_CLIENT_ID` / `SPOTIPY_CLIENT_SECRET` names required by upstream libraries.

### `songs.json`
Place a JSON file in the project root with Spotify URLs or combined Spotify/YouTube mappings.

Example:
```json
{
  "Song Title": "https://open.spotify.com/track/..."
}
```

---

## Running the Project

### Run the downloader
```powershell
cd C:\dev\Python\spotdl
.\venv\Scripts\python.exe -m youtube_mp3_puller
```

### Run the GUI
```powershell
.\venv\Scripts\python.exe youtube_mp3_puller_ui.py
```

### Activate the venv first (optional)
```powershell
.\venv\Scripts\Activate.ps1
python -m youtube_mp3_puller
```

---

## Project Structure

- `youtube_mp3_puller/__main__.py` — package entrypoint for `python -m youtube_mp3_puller`
- `youtube_mp3_puller/` — refactored package containing the core logic
  - `core.py` — orchestrates download preparation and fallback strategies
  - `env_utils.py` — loads `.env` and configures Spotify credentials
  - `spotify_helpers.py` — Spotify URL normalization and playlist loading
  - `youtube_helpers.py` — YouTube URL handling, search, and song normalization
  - `json_loader.py` — loads song definitions from JSON files
  - `downloader.py` — download orchestration and FFmpeg support
  - `cli.py` — interactive command-line prompts
  - `types.py` — shared request and option models
- `youtube_mp3_puller_ui.py` — optional GUI frontend
- `downloads/` — download output directory
- `.env` — optional Spotify credential configuration
- `songs.json` — user-provided song definitions

---

## Design Patterns

- **Facade:** The top-level module and package export provide a simple stable API while hiding internal complexity.
- **Single Responsibility:** Each module handles one concern: env loading, Spotify/YouTube resolution, JSON parsing, download orchestration, or CLI interaction.
- **Adapter:** The code adapts upstream SpotDL and yt-dlp interfaces into a consistent internal download workflow.
- **Strategy:** Playlist handling uses multiple resolution strategies, including native playlist support, Spotify API fallback, and Spotify web scraping.

---

## Troubleshooting

### Spotify auth fails
Ensure `.env` contains valid credentials. The code maps Spotify credentials into the compatible environment names required by upstream libraries.

### FFmpeg problems
Verify `ffmpeg.exe` is available in the virtual environment `Scripts` folder or on PATH.

### Downloads not appearing
Check that `songs.json` is valid JSON and that the requested URLs are accessible.
