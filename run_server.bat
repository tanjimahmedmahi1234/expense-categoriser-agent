@echo off
cd /d "%~dp0"
if not exist .env (
    echo No .env file found. Copy .env.example to .env and put your OpenAI key in it.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
echo Starting the API. Open http://127.0.0.1:8000 in your browser.
echo Press Ctrl+C in this window to stop it.
python -m uvicorn app.main:app --reload
pause
