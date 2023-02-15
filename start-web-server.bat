@echo off

setlocal EnableDelayedExpansion

rem Check Python version
set required_version=3.8.0
for /f "tokens=1-3" %%a in ('python --version 2^>^&1') do (
    set py_major=%%b
    set py_minor=%%c
)
if "!py_major!" NEQ "Python" (
    echo Error: Python is not installed.
    pause
    exit /b 1
)
if "!py_minor!" LSS "%required_version%" (
    echo Error: This script requires Python %required_version% or later.
    pause
    exit /b 1
)

rem Check for virtual environment
set env_dir=web-server\env
if not exist !env_dir! (
    echo Creating virtual environment...
    python -m venv !env_dir!
)

rem Activate virtual environment
call !env_dir!\Scripts\activate.bat

rem Install packages
echo Installing packages...
if not exist web-server\requirements.txt (
    echo Error: requirements.txt file not found.
    pause
    exit /b 1
)
pip install -r web-server\requirements.txt
if errorlevel 1 (
    echo Error: Failed to install required packages.
    pause
    exit /b 1
)

rem Start web server
echo Starting web server...
python web-server\src\main.py

endlocal
