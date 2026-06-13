# spotdl Project - Quick Reference

## Essential Commands

### Create the virtual environment
```powershell
cd C:\dev\Python\spotdl
python -m venv .venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
Or run:
```powershell
setup_venv.bat
```

### Run the downloader
```powershell
cd C:\dev\Python\spotdl
.\venv\Scripts\python.exe -m youtube_mp3_puller
```

### Run the GUI
```powershell
.\venv\Scripts\python.exe youtube_mp3_puller_ui.py
```

### Activate venv (optional)
```powershell
.\venv\Scripts\Activate.ps1
python -m youtube_mp3_puller
```

### Check FFmpeg
```powershell
.\venv\Scripts\ffmpeg.exe -version
```

### List installed packages
```powershell
.\venv\Scripts\python.exe -m pip list
```

### Update a package
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade spotdl
```

## Configuration Files

### songs.json (required)
Place in `C:\dev\Python\spotdl\songs.json`
```json
{
  "Song Title": "https://open.spotify.com/track/...",
  "Another Song": "https://open.spotify.com/track/..."
}
```

### .env (optional)
Place in `C:\dev\Python\spotdl\.env`
```
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```

## Output Location
Downloads: `C:\dev\Python\spotdl\downloads`

## Known Issues
- Metadata tagging may fail for some songs (file still downloads)
- Spotify rate limiting after ~5 hours of continuous requests
- Some songs may not have YouTube matches

## Documentation
See `PROJECT_SUMMARY.md` for full details.
