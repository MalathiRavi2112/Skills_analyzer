@echo off
title SkillGap Backend API (Port 5000)
cd /d "%~dp0backend"

if not exist node_modules (
    echo [1/3] Installing backend npm packages...
    call npm install
)

echo [2/3] Seeding database with sample jobs and courses...
call npm run seed
if errorlevel 1 (
    echo.
    echo [Notice] Database seeding skipped because MongoDB is not connected yet.
    echo Please make sure MongoDB is running or update MONGO_URI in backend\.env
    echo.
)

echo [3/3] Starting Node.js Express server on http://localhost:5000 ...
call npm run dev
pause
