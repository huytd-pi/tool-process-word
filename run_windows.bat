@echo off
chcp 65001 >nul
title DocxMath Studio - Dang Chay Tren Cong 8000
echo ==========================================================
echo        DocxMath Studio - Word Equation (OMML) Tool
echo ==========================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 1. Kiem tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python tren he thong!
    echo Vui long cai dat Python 3.10+ tu https://www.python.org/
    echo - Luu y quan trong: Nho tich chon "Add Python to PATH" khi cai dat.
    echo.
    pause
    exit /b 1
)

REM 2. Cap nhat PATH de tim Pandoc neu duoc cai vao AppData
set "PATH=%LOCALAPPDATA%\Pandoc;C:\Program Files\Pandoc;%PATH%"

REM Kiem tra Pandoc
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo [CANH BAO] Khong tim thay Pandoc trong PATH!
    echo Ban co the cai dat Pandoc bang lenh: winget install JohnMacFarlane.Pandoc
    echo.
) else (
    echo [OK] Pandoc da san sang.
)

REM 3. Kiem tra va cai dat thu vien Python
echo.
echo [1/3] Kiem tra thu vien Python can thiet...
python -m pip install -r backend\requirements.txt --quiet
if errorlevel 1 (
    echo [CANH BAO] Co loi khi cai dat thu vien Python qua pip. Dang thu tiep tuc...
)

REM 4. Kiem tra ban bien dich Frontend
echo [2/3] Kiem tra giao dien nguoi dung...
if not exist "frontend\dist\index.html" (
    echo [!] Chua tim thay ban build frontend. Dang tien hanh bien dich...
    cd frontend
    call npm install --quiet
    call npm run build
    cd ..
) else (
    echo [OK] Ban bien dich frontend da san sang.
)

REM 5. Khoi dong FastAPI Server
echo.
echo [3/3] Dang khoi dong may chu tai http://localhost:8000 ...
echo ==========================================================
echo  Trinh duyet se tu dong mo trang web.
echo  De tat may chu, vui long nhan Ctrl+C trong cua so nay.
echo ==========================================================
echo.

set "PYTHONPATH=%SCRIPT_DIR%backend;%SCRIPT_DIR%"

REM Mo trinh duyet sau khi khoi dong
start "" "http://localhost:8000"

REM Chay Uvicorn truc tiep
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

echo.
echo ==========================================================
echo May chu DocxMath Studio da dung lai.
echo ==========================================================
pause
