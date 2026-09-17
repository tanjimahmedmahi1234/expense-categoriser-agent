@echo off
cd /d "%~dp0"
if not exist .env (
    echo No .env file found. Copy .env.example to .env and put your OpenAI key in it.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
if not exist evaluation mkdir evaluation
echo Running 11 cases x 2 repeats for prompts v1 v2 v3 with a pause between runs.
echo About 8 minutes. Do not close this window.
python -m scripts.evaluate --versions v1 v2 v3 --repeats 2 --pause 5
pause
