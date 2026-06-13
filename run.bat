@echo off
REM Activate the virtual environment
call .\venv\Scripts\activate
REM Run the YouTube MP3 Puller package
python -m youtube_mp3_puller
pause