@echo off
chcp 65001 >nul
title DocxMath Studio - Running on port 8000
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ==========================================================
echo        DocxMath Studio - Word Equation (OMML) Tool
echo ==========================================================
echo.

REM 1. Update PATH to include typical Pandoc and Python locations
set "PATH=%LOCALAPPDATA%\Pandoc;C:\Program Files\Pandoc;%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python310;C:\Program Files\Python313;C:\Program Files\Python312;C:\Program Files\Python311;C:\Program Files\Python310;%PATH%"

REM 2. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    py -3 --version >nul 2>&1
    if errorlevel 1 (
        echo [!] Python is not found or not in PATH.
        echo Launching automated setup...
        echo.
        call "%SCRIPT_DIR%setup_windows.bat"
        exit /b 0
    )
)

REM 3. Check Pandoc
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo [!] Pandoc is not found in PATH.
    echo Launching automated setup...
    echo.
    call "%SCRIPT_DIR%setup_windows.bat"
    exit /b 0
)

REM 4. Check Frontend Web Bundle
if not exist "frontend\dist\index.html" (
    echo [!] Frontend build not found.
    echo Launching automated setup...
    call "%SCRIPT_DIR%setup_windows.bat"
    exit /b 0
)

REM 5. Check Python dependencies
python -c "import fastapi, docx, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing required Python libraries...
    python -m pip install -r backend\requirements.txt --quiet
)

REM 6. Start FastAPI server and open browser
echo.
echo [OK] All components are ready!
echo Starting local server at http://localhost:8000 ...
echo ==========================================================
echo  Your web browser will open automatically.
echo  To stop the application, press Ctrl+C in this window.
echo ==========================================================
echo.

set "PYTHONPATH=%SCRIPT_DIR%backend;%SCRIPT_DIR%"

REM Open browser
start "" "http://localhost:8000"

REM Run Uvicorn directly
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

echo.
echo ==========================================================
echo DocxMath Studio server has stopped.
echo ==========================================================
pause
