@echo off
REM Create a local virtual environment and install dependencies
python -m venv .venv
call .\venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pause
