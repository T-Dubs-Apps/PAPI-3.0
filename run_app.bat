@echo off
title PAPI 3.0-1 — AI Trader Launcher
color 0A
echo ============================================
echo   PAPI 3.0-1  ^|  AI Trader App Launcher
echo ============================================
echo.

REM Check that Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/3] Python found.

REM Install / upgrade dependencies
echo [2/3] Installing dependencies (this only takes a moment)...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements. Check your internet connection.
    pause
    exit /b 1
)

echo [3/3] Launching PAPI 3.0-1...
echo.
echo The app will open in your browser automatically.
echo Press Ctrl+C in this window to stop the app.
echo.
python -m streamlit run app.py
pause
