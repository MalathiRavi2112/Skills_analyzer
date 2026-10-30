@echo off
title SkillGap Analyzer Launcher
cd /d "%~dp0"

echo =========================================================
echo    Launching SkillGap Analyzer (3 Microservices)
echo =========================================================
echo.
echo Starting Python NLP Microservice (Port 8000)...
start "SkillGap NLP Service" cmd /k run-nlp.bat

timeout /t 3 /nobreak >nul

echo Starting Node.js Backend API (Port 5000)...
start "SkillGap Backend API" cmd /k run-backend.bat

timeout /t 3 /nobreak >nul

echo Starting React Vite Frontend (Port 5173)...
start "SkillGap Frontend UI" cmd /k run-frontend.bat

echo.
echo =========================================================
echo All 3 services are launching in their own windows!
echo Once ready, open your browser at: http://localhost:5173
echo =========================================================

