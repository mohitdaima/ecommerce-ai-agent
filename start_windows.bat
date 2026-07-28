@echo off
REM ===================================================================
REM  E-Commerce AI Team - Windows launcher
REM  Just DOUBLE-CLICK this file. No command prompt typing needed.
REM ===================================================================
title E-Commerce AI Team
cd /d "%~dp0"

echo.
echo   Starting your E-Commerce AI Team...
echo   (First time may take a minute to install helpers.)
echo.

REM Find Python (try 'python', then 'py')
where python >nul 2>nul
if %errorlevel%==0 (
    set PY=python
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set PY=py
    ) else (
        echo   Python was not found. Please install it from https://python.org/downloads
        echo   and tick "Add Python to PATH" during install, then run this again.
        echo.
        pause
        exit /b
    )
)

REM Install helper libraries (quietly). Safe to run every time.
%PY% -m pip install -q -r requirements.txt

REM Launch the web app (it opens your browser automatically)
%PY% web.py

echo.
echo   The app has stopped. You can close this window.
pause
