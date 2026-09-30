@echo off
chcp 65001 >nul
title DocxMath Studio - Cai Dat Moi Truong Tu Dong
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ==========================================================
echo        DocxMath Studio - Trình Cài Đặt Tự Động
echo ==========================================================
echo.
echo Đang chuẩn bị kiểm tra và cài đặt các thành phần cần thiết:
echo  1. Pandoc (Xử lý công thức Toán Word Equation OMML)
echo  2. Python 3.10+ (FastAPI Backend)
echo  3. Các thư viện Python (python-docx, uvicorn...)
echo  4. Giao diện Web DocxMath Studio
echo.
echo Quá trình này hoàn toàn tự động, vui lòng chờ trong giây lát...
echo ==========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\setup_environment.ps1"

if errorlevel 1 (
    echo.
    echo [THONG BAO] Qua trinh cai dat ket thuc.
    pause
)
