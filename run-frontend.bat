@echo off
title SkillGap Frontend (Port 5173)
cd /d "%~dp0frontend"

if not exist node_modules (
    echo [1/2] Installing frontend npm packages...
    call npm install
)

echo [2/2] Starting React Vite dev server on http://localhost:5173 ...
call npm run dev
pause

