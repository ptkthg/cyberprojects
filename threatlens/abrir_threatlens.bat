@echo off
setlocal
cd /d %~dp0

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python launcher.py
if errorlevel 1 (
    echo.
    echo Erro ao executar launcher.py
    pause
)
endlocal
