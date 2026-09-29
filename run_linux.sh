#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "       DocxMath Studio - Word Equation (OMML) Tool"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[LỖI] Không tìm thấy python3. Vui lòng chạy: sudo apt update && sudo apt install -y python3 python3-pip"
    exit 1
fi

# Check Pandoc
if ! command -v pandoc &> /dev/null; then
    echo "[CẢNH BÁO] Không tìm thấy Pandoc. Vui lòng cài đặt: sudo apt install -y pandoc"
fi

# Check Node
if ! command -v npm &> /dev/null; then
    echo "[CẢNH BÁO] Không tìm thấy npm để build frontend. Kiểm tra thư mục frontend/dist..."
fi

echo "[1/3] Cài đặt dependencies Python..."
python3 -m pip install -r backend/requirements.txt --quiet

echo "[2/3] Kiểm tra giao diện người dùng..."
if [ ! -f "frontend/dist/index.html" ]; then
    echo "Biên dịch frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
else
    echo "[OK] Bản build frontend đã sẵn sàng."
fi

echo ""
echo "[3/3] Đang khởi động máy chủ tại http://localhost:8000 ..."
export PYTHONPATH="$SCRIPT_DIR/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
