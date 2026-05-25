#!/usr/bin/env bash
# PAPI 3.0-1 — AI Trader App Launcher (Mac / Linux)
set -e

echo "============================================"
echo "  PAPI 3.0-1  |  AI Trader App Launcher"
echo "============================================"
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "  Mac:   brew install python  (or https://www.python.org/downloads/)"
    echo "  Linux: sudo apt install python3 python3-pip"
    exit 1
fi
echo "[1/3] Python found: $(python3 --version)"

# Install dependencies
echo "[2/3] Installing dependencies..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r requirements.txt

echo "[3/3] Launching PAPI 3.0-1..."
echo
echo "The app will open at http://localhost:8501 — open that URL in your browser."
echo "Press Ctrl+C to stop the app."
echo

python3 -m streamlit run app.py
