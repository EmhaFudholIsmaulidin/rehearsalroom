#!/usr/bin/env bash
# ============================================================
#  RehearsalRoom - cukup Python, tidak perlu Node/PostgreSQL
#  Jalankan:  ./start.sh   (pertama kali: chmod +x start.sh)
# ============================================================
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/rehearsalroom-backend"

if [ ! -d "venv" ]; then
  echo "[Setup] Membuat virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
  echo "[Setup] Install dependencies (sekali saja, mohon tunggu)..."
  pip install --upgrade pip >/dev/null
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

echo ""
echo " ============================================"
echo "  RehearsalRoom siap!"
echo "  Database SQLite + data dummy dibuat otomatis."
echo "  Buka browser ke:  http://localhost:8000"
echo "  Tekan CTRL+C untuk berhenti."
echo " ============================================"
echo ""

( sleep 2 && (command -v xdg-open >/dev/null && xdg-open http://localhost:8000 || open http://localhost:8000) ) >/dev/null 2>&1 &
uvicorn app.main:app --host 0.0.0.0 --port 8000
