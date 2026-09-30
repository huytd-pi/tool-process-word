@echo off
chcp 65001 >nul
title DocxMath Studio - Dang Chay Tren Cong 8000
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ==========================================================
echo        DocxMath Studio - Word Equation (OMML) Tool
echo ==========================================================
echo.

REM 1. Cap nhat PATH he thong
set "PATH=%LOCALAPPDATA%\Pandoc;C:\Program Files\Pandoc;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python310;C:\Program Files\Python312;C:\Program Files\Python311;C:\Program Files\Python310;%PATH%"

REM 2. Kiem tra Python
python --version >nul 2>&1
if errorlevel 1 (
    py -3 --version >nul 2>&1
    if errorlevel 1 (
        echo [!] Chua tim thay Python hoac moi truong chua duoc thiet lap.
        echo Dang tu dong khoi chay trinh cai dat moi truong tu dong...
        echo.
        call "%SCRIPT_DIR%cai_dat_windows.bat"
        exit /b 0
    )
)

REM 3. Kiem tra Pandoc
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo [!] Chua tim thay Pandoc tren may.
    echo Dang tu dong khoi chay trinh cai dat moi truong...
    echo.
    call "%SCRIPT_DIR%cai_dat_windows.bat"
    exit /b 0
)

REM 4. Kiem tra ban bien dich Frontend
if not exist "frontend\dist\index.html" (
    echo [!] Chua tim thay ban build giao dien nguoi dung.
    echo Dang tien hanh cai dat va bien dich...
    call "%SCRIPT_DIR%cai_dat_windows.bat"
    exit /b 0
)

REM 5. Kiem tra nhanh thu vien Python
python -c "import fastapi, docx, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [!] Dang cai dat bo sung cac thu vien Python con thieu...
    python -m pip install -r backend\requirements.txt --quiet
)

REM 6. Khoi dong FastAPI Server va mo trinh duyet
echo.
echo [OK] Tat ca thanh phan da san sang!
echo Dang khoi dong may chu tai http://localhost:8000 ...
echo ==========================================================
echo  Trinh duyet web se tu dong mo ung dung.
echo  De tat ung dung, vui long nhan Ctrl+C trong cua so nay.
echo ==========================================================
echo.

set "PYTHONPATH=%SCRIPT_DIR%backend;%SCRIPT_DIR%"

REM Mo trinh duyet
start "" "http://localhost:8000"

REM Chay Uvicorn truc tiep
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

echo.
echo ==========================================================
echo May chu DocxMath Studio da dung lai.
echo ==========================================================
pause
