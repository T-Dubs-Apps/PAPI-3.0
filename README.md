# P.A.P.I. 3.0-1

**Programmable Artificial Personal Intelligence**

A Streamlit-based AI personal assistant featuring a full **AI Trader** module with live stock data, candlestick charts, moving-average + RSI signals, and a portfolio tracker.

---

## 🚀 Run on Your Computer (Windows / Mac / Linux)

> **Requirements:** Python 3.10 or newer — download from https://www.python.org/downloads/

### Windows (easiest)
1. Download / clone this repository as a ZIP and unzip it.
2. Double-click **`run_app.bat`** — it installs everything and opens the app in your browser automatically.

### Mac / Linux
```bash
chmod +x run_app.sh
./run_app.sh
```

### Manual setup
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open **http://localhost:8501** in your browser.

---

## 📈 AI Trader Features

- **Live stock data** via yfinance (falls back to realistic simulation if offline)
- **Candlestick chart** with SMA 20 / SMA 50 overlays
- **RSI (14) indicator** with overbought/oversold zones
- **AI Signal** — BUY / SELL / HOLD based on SMA crossover + RSI
- **Portfolio tracker** — buy & sell shares, track P&L in real time
- **Trade history** log

---

## ☁️ Deploy to Render (free hosting — shareable link)

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com), create a free account, and click **New → Web Service**.
3. Connect your GitHub repo — Render will auto-detect `render.yaml`.
4. Click **Deploy**. Once live you'll get a public URL you can share.

Manual settings (if needed):
| Field | Value |
|-------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |
| Python Version | `3.11.0` |

---

> ⚠️ **Disclaimer:** AI Trader signals are for educational/entertainment purposes only and are not financial advice.
