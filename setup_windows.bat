@echo off
chcp 65001 >nul
title DocxMath Studio - Automated Windows Setup
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ==========================================================
echo        DocxMath Studio - Automated Windows Setup
echo ==========================================================
echo.
echo Preparing automated environment setup:
echo  1. Pandoc (Required for Word Equation OMML export)
echo  2. Python 3.10+ (FastAPI Backend)
echo  3. Python requirements (fastapi, python-docx, uvicorn...)
echo  4. Pre-built Frontend Web UI
echo.
echo Setup is running automatically, please wait a moment...
echo ==========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\setup_environment.ps1"

if errorlevel 1 (
    echo.
    echo [INFO] Setup finished.
    pause
)
