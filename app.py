import streamlit as st
import time
import os
import warnings
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from gTTS import gTTS
from textblob import TextBlob

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# ---------------------------------------------------------
# CONFIG & SETUP
# ---------------------------------------------------------
warnings.filterwarnings("ignore", category=SyntaxWarning)

st.set_page_config(
    page_title="PAPI 3.0-1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CORE FUNCTIONS
# ---------------------------------------------------------

# ---------------------------------------------------------
# AI TRADER — DATA & ANALYSIS
# ---------------------------------------------------------

SIMULATED_DATA = {
    "AAPL": {"name": "Apple Inc.", "base": 185.0},
    "TSLA": {"name": "Tesla Inc.", "base": 248.0},
    "MSFT": {"name": "Microsoft Corp.", "base": 415.0},
    "NVDA": {"name": "NVIDIA Corp.", "base": 870.0},
    "AMZN": {"name": "Amazon.com Inc.", "base": 182.0},
    "GOOGL": {"name": "Alphabet Inc.", "base": 172.0},
    "META": {"name": "Meta Platforms Inc.", "base": 510.0},
    "SPY": {"name": "S&P 500 ETF", "base": 535.0},
}


def _make_simulated_df(ticker: str, periods: int = 90) -> pd.DataFrame:
    """Generate realistic-looking simulated OHLCV data."""
    import numpy as np
    base = SIMULATED_DATA.get(ticker.upper(), {"base": 100.0})["base"]
    rng = np.random.default_rng(abs(hash(ticker)) % (2**31))
    dates = pd.date_range(end=pd.Timestamp.today(), periods=periods, freq="B")
    prices = [base]
    for _ in range(periods - 1):
        prices.append(prices[-1] * (1 + rng.normal(0.0003, 0.015)))
    closes = pd.Series(prices)
    highs = closes * (1 + rng.uniform(0, 0.015, periods))
    lows = closes * (1 - rng.uniform(0, 0.015, periods))
    opens = closes.shift(1).fillna(closes.iloc[0])
    volumes = rng.integers(5_000_000, 50_000_000, periods)
    df = pd.DataFrame({"Open": opens.values, "High": highs, "Low": lows,
                       "Close": closes.values, "Volume": volumes}, index=dates)
    return df


def fetch_stock_data(ticker: str, period: str = "3mo"):
    """Fetch stock data from yfinance with simulated fallback."""
    if YFINANCE_AVAILABLE:
        try:
            data = yf.download(ticker, period=period, auto_adjust=True, progress=False)
            if data is not None and len(data) > 10:
                data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
                return data, "live"
        except Exception:
            pass
    return _make_simulated_df(ticker), "simulated"


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add SMA20, SMA50, and RSI14 columns to the dataframe."""
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("nan"))
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def generate_signal(df: pd.DataFrame):
    """Return (signal, reasoning, confidence) based on SMA crossover + RSI."""
    clean = df.dropna(subset=["SMA20", "SMA50", "RSI"])
    if len(clean) < 2:
        return "🟡 HOLD", "Not enough data for analysis.", 0.50
    last = clean.iloc[-1]
    prev = clean.iloc[-2]

    sma_cross_up = prev["SMA20"] <= prev["SMA50"] and last["SMA20"] > last["SMA50"]
    sma_cross_down = prev["SMA20"] >= prev["SMA50"] and last["SMA20"] < last["SMA50"]
    sma_bullish = last["SMA20"] > last["SMA50"]
    rsi = last["RSI"]

    if sma_cross_up or (sma_bullish and rsi < 45):
        if rsi < 30:
            return "🟢 STRONG BUY", f"SMA20 above SMA50 + RSI oversold ({rsi:.1f})", 0.90
        return "🟢 BUY", f"SMA20 crossing above SMA50, RSI at {rsi:.1f}", 0.75

    if sma_cross_down or (not sma_bullish and rsi > 65):
        if rsi > 75:
            return "🔴 STRONG SELL", f"SMA20 below SMA50 + RSI overbought ({rsi:.1f})", 0.88
        return "🔴 SELL", f"SMA20 crossing below SMA50, RSI at {rsi:.1f}", 0.72

    return "🟡 HOLD", f"No clear crossover signal. RSI at {rsi:.1f}", 0.60


def build_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Build a two-panel Plotly chart: price (with SMAs) + RSI."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.03,
        subplot_titles=(f"{ticker} — Price & Moving Averages", "RSI (14)")
    )
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price",
        increasing_line_color="#00C853", decreasing_line_color="#D50000"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA 20",
                             line=dict(color="#1E88E5", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA 50",
                             line=dict(color="#FB8C00", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                             line=dict(color="#AB47BC", width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1,
                  annotation_text="Overbought", annotation_position="bottom right")
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1,
                  annotation_text="Oversold", annotation_position="top right")
    fig.update_layout(
        template="plotly_dark", height=550,
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=1.08)
    )
    return fig


# ---------------------------------------------------------
# CORE FUNCTIONS
# ---------------------------------------------------------

def speak_text(text):
    """
    Converts text to speech using gTTS and plays it.
    Uses a try/except block to prevent app crashes if audio fails.
    """
    if not text.strip():
        return

    try:
        tts = gTTS(text=text, lang='en')
        # Save to a generic filename to avoid clutter
        filename = "temp_voice.mp3"
        tts.save(filename)
        
        # Open the file and read bytes so Streamlit can play it safely
        with open(filename, "rb") as f:
            audio_bytes = f.read()
        
        # Display audio player (visible to allow replay)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
        
    except Exception as e:
        # Log error to console but keep UI clean
        print(f"Audio error: {e}")
        st.toast("Audio output unavailable (Text mode only)")

def execute_app_simulation(app_name):
    """
    Simulates the execution of a sub-app on screen with a visual loader.
    """
    st.divider()
    st.subheader(f"🚀 Executing: {app_name}")
    
    # Visual Progress Bar
    progress_text = f"Initializing {app_name} protocols..."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(0.5)
    my_bar.empty()
    
    # Status Indicators
    with st.status("System Check", expanded=True) as status:
        st.write("Loading Aegis Security protocols...")
        time.sleep(0.5)
        st.write("Verifying User Permissions...")
        time.sleep(0.5)
        st.write(f"Launching {app_name} interface...")
        time.sleep(0.5)
        status.update(label=f"{app_name} is Ready", state="complete", expanded=False)
    
    # Success Message
    st.success(f"Active Session: {app_name}")
    
    # Dummy Interface based on app name
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 🖥️")
    with col2:
        if "security" in app_name.lower():
            st.info("🛡️ **Aegis Guard**: Monitoring active threats. \n\nStatus: **System Safe**.")
        elif "audio" in app_name.lower():
            st.info("🎛️ **Audio Workbench**: Input channels open. \n\nFrequency: **44.1kHz**.")
        elif "stock" in app_name.lower():
            st.info("📈 **Market Data Link**: Connection Established. \n\nData Feed: **Live**.")
        else:
            st.info(f"System: **{app_name}** is running in the main viewport.")

# ---------------------------------------------------------
# UI LAYOUT
# ---------------------------------------------------------

# Sidebar
with st.sidebar:
    st.title("PAPI 3.0-1")
    st.caption("System Interface")
    st.markdown("---")
    st.write("**System Status:** 🟢 Online")
    st.write("**Security:** 🛡️ Aegis Guard Active")
    st.write("**User:** Troy Walker")

    st.markdown("### Quick Commands")
    if st.button("Activate Children's Mode"):
        st.toast("Children's Mode Activated. Parental Controls Locked.")
    if st.button("Run Diagnostics"):
        with st.spinner("Scanning system files..."):
            time.sleep(1.5)
        st.toast("All systems nominal.")

    st.markdown("---")
    data_src = "🌐 Live" if YFINANCE_AVAILABLE else "🔁 Simulated"
    st.caption(f"Trader data source: {data_src}")

# Main header
st.title("P.A.P.I. 3.0-1")
st.markdown("**Programmable Artificial Personal Intelligence**")

tab_papi, tab_trader = st.tabs(["🤖 PAPI Command Center", "📈 AI Trader"])

# ── TAB 1: PAPI COMMAND CENTER ──────────────────────────────────────────────
with tab_papi:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Enter command or chat with PAPI...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response_text = ""
        run_app_trigger = False
        target_app = ""
        user_input_lower = user_input.lower()

        if "execute" in user_input_lower or "run" in user_input_lower:
            words = user_input.split()
            keyword = "execute" if "execute" in user_input_lower else "run"
            try:
                lower_words = [w.lower() for w in words]
                if keyword in lower_words:
                    idx = lower_words.index(keyword)
                    if idx + 1 < len(words):
                        target_app = " ".join(words[idx + 1:]).capitalize()
                        response_text = f"Acknowledged. Initiating launch sequence for {target_app}."
                        run_app_trigger = True
                    else:
                        response_text = "Which application would you like me to execute?"
            except Exception:
                response_text = "I couldn't identify the application name."
        elif "hello" in user_input_lower:
            response_text = "Greetings, Troy. Systems are online and awaiting your command."
        elif "status" in user_input_lower:
            response_text = "All systems operational. Battery at 98%. Security active."
        else:
            response_text = f"Processing command: {user_input}"

        with st.chat_message("assistant"):
            st.markdown(response_text)
            speak_text(response_text)
            if run_app_trigger:
                execute_app_simulation(target_app)

        st.session_state.messages.append({"role": "assistant", "content": response_text})

# ── TAB 2: AI TRADER ────────────────────────────────────────────────────────
with tab_trader:
    st.subheader("📈 AI Trader — Market Analysis & Signals")
    st.caption(
        "Powered by SMA crossover + RSI strategy. "
        + ("Live data via yfinance." if YFINANCE_AVAILABLE else
           "⚠️ yfinance unavailable — using simulated data.")
    )

    # ── Session state init ──────────────────────────────────────────────────
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {}   # {ticker: {"shares": int, "avg_cost": float}}
    if "trade_log" not in st.session_state:
        st.session_state.trade_log = []

    # ── Stock Analysis panel ────────────────────────────────────────────────
    col_input, col_period = st.columns([2, 1])
    with col_input:
        ticker_input = st.text_input(
            "Stock Ticker Symbol", value="AAPL",
            placeholder="e.g. AAPL, TSLA, MSFT, NVDA"
        ).upper().strip()
    with col_period:
        period_map = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
        period_label = st.selectbox("Period", list(period_map.keys()), index=1)
        selected_period = period_map[period_label]

    analyze_btn = st.button("🔍 Analyze", use_container_width=True, type="primary")

    if "trader_ticker" not in st.session_state:
        st.session_state.trader_ticker = "AAPL"
    if "trader_df" not in st.session_state:
        st.session_state.trader_df = None
    if "trader_source" not in st.session_state:
        st.session_state.trader_source = ""

    if analyze_btn and ticker_input:
        with st.spinner(f"Fetching data for {ticker_input}..."):
            df_raw, source = fetch_stock_data(ticker_input, selected_period)
            df_ind = compute_indicators(df_raw)
        st.session_state.trader_ticker = ticker_input
        st.session_state.trader_df = df_ind
        st.session_state.trader_source = source

    df = st.session_state.trader_df
    current_ticker = st.session_state.trader_ticker

    if df is None:
        # Auto-load AAPL on first visit
        with st.spinner("Loading default data..."):
            df_raw, source = fetch_stock_data("AAPL", "3mo")
            df = compute_indicators(df_raw)
            st.session_state.trader_df = df
            st.session_state.trader_source = source

    if df is not None and len(df) > 0:
        # ── Key metrics ─────────────────────────────────────────────────────
        current_price = float(df["Close"].iloc[-1])
        prev_price = float(df["Close"].iloc[-2]) if len(df) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price * 100) if prev_price else 0
        arrow = "▲" if change >= 0 else "▼"
        color = "green" if change >= 0 else "red"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Price", f"${current_price:.2f}",
                  f"{arrow} {abs(change):.2f} ({abs(change_pct):.2f}%)")
        m2.metric("SMA 20", f"${df['SMA20'].dropna().iloc[-1]:.2f}"
                  if not df["SMA20"].dropna().empty else "—")
        m3.metric("SMA 50", f"${df['SMA50'].dropna().iloc[-1]:.2f}"
                  if not df["SMA50"].dropna().empty else "—")
        rsi_val = df["RSI"].dropna().iloc[-1] if not df["RSI"].dropna().empty else None
        m4.metric("RSI (14)", f"{rsi_val:.1f}" if rsi_val is not None else "—")

        # ── AI Signal ───────────────────────────────────────────────────────
        signal, reasoning, confidence = generate_signal(df)
        sig_color = "#00C853" if "BUY" in signal else ("#D50000" if "SELL" in signal else "#FFC107")
        st.markdown(
            f"""
            <div style="background:{sig_color}22;border-left:5px solid {sig_color};
                        padding:12px 16px;border-radius:6px;margin:12px 0;">
                <h3 style="margin:0;color:{sig_color};">{signal}</h3>
                <p style="margin:4px 0 0 0;color:#ccc;">{reasoning}</p>
                <small style="color:#aaa;">Confidence: {confidence*100:.0f}%</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Chart ────────────────────────────────────────────────────────────
        st.plotly_chart(build_chart(df, current_ticker), use_container_width=True)

        # ── Trade execution ──────────────────────────────────────────────────
        st.markdown("### 💼 Execute Trade")
        t1, t2, t3, t4 = st.columns([2, 1, 1, 1])
        with t1:
            trade_ticker = st.text_input(
                "Ticker", value=current_ticker, key="trade_ticker_input"
            ).upper().strip()
        with t2:
            shares_input = st.number_input("Shares", min_value=1, value=10, step=1)
        with t3:
            if st.button("🟢 BUY", use_container_width=True):
                cost = current_price * shares_input
                port = st.session_state.portfolio
                if trade_ticker in port:
                    total_shares = port[trade_ticker]["shares"] + shares_input
                    avg = (port[trade_ticker]["avg_cost"] * port[trade_ticker]["shares"]
                           + cost) / total_shares
                    port[trade_ticker] = {"shares": total_shares, "avg_cost": avg}
                else:
                    port[trade_ticker] = {"shares": shares_input, "avg_cost": current_price}
                st.session_state.trade_log.append(
                    f"BUY {shares_input} {trade_ticker} @ ${current_price:.2f}"
                )
                st.toast(f"✅ Bought {shares_input} shares of {trade_ticker} @ ${current_price:.2f}")
        with t4:
            if st.button("🔴 SELL", use_container_width=True):
                port = st.session_state.portfolio
                if trade_ticker in port and port[trade_ticker]["shares"] >= shares_input:
                    port[trade_ticker]["shares"] -= shares_input
                    if port[trade_ticker]["shares"] == 0:
                        del port[trade_ticker]
                    st.session_state.trade_log.append(
                        f"SELL {shares_input} {trade_ticker} @ ${current_price:.2f}"
                    )
                    st.toast(f"✅ Sold {shares_input} shares of {trade_ticker} @ ${current_price:.2f}")
                else:
                    st.toast(f"⚠️ Not enough shares of {trade_ticker} to sell.")

        # ── Portfolio ────────────────────────────────────────────────────────
        st.markdown("### 📊 Portfolio")
        port = st.session_state.portfolio
        if port:
            rows = []
            for sym, pos in port.items():
                # Try to get live price; fall back to avg cost
                try:
                    live_df, _ = fetch_stock_data(sym, "5d")
                    live_price = float(live_df["Close"].iloc[-1])
                except Exception:
                    live_price = pos["avg_cost"]
                mkt_val = live_price * pos["shares"]
                cost_basis = pos["avg_cost"] * pos["shares"]
                pnl = mkt_val - cost_basis
                rows.append({
                    "Ticker": sym,
                    "Shares": pos["shares"],
                    "Avg Cost": f"${pos['avg_cost']:.2f}",
                    "Live Price": f"${live_price:.2f}",
                    "Market Value": f"${mkt_val:,.2f}",
                    "P&L": f"${pnl:+,.2f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No positions yet. Use the trade panel above to add stocks.")

        # ── Trade log ────────────────────────────────────────────────────────
        if st.session_state.trade_log:
            with st.expander("📋 Trade History"):
                for entry in reversed(st.session_state.trade_log):
                    st.write(f"• {entry}")

        # ── Disclaimer ───────────────────────────────────────────────────────
        st.caption(
            "⚠️ **Disclaimer:** This app is for educational/entertainment purposes only. "
            "Signals are based on simple technical indicators and are NOT financial advice. "
            "Always do your own research before trading real money."
        )