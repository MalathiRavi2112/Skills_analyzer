@echo off
title SkillGap NLP Microservice (Port 8000)
cd /d "%~dp0nlp-service"

if not exist venv (
    echo [1/3] Creating Python virtual environment...
    python -m venv venv
)

echo [2/3] Activating virtual environment & installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo [3/3] Starting FastAPI NLP Microservice on http://localhost:8000 ...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause

