@echo off

cd web-server\env\Scripts
call activate.bat
cd ..\..

set "requirements_installed=true"
for /f "delims=" %%i in (web-server\requirements.txt) do (
    pip list --format=freeze | findstr /i /C:"%%i" >nul
    if errorlevel 1 (
        set "requirements_installed=false"
        pip install "%%i"
    )
)

if "%requirements_installed%"=="false" (
    pip install -r web-server\requirements.txt
)

cd web-server\src
python main.py
