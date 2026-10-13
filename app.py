import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="AI Quant Terminal", page_icon="⚡", layout="wide")

st.title("⚡ AI Quant Terminal & Market Command Center")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Quant Analysis & Risk", 
    "⚔️ Stock Comparison Matrix", 
    "📊 Market Sentiment Meter", 
    "🚀 Live IPOs", 
    "📚 Knowledge Hub"
])

# --- TAB 1: QUANT ANALYSIS & RISK CALCULATOR ---
with tab1:
    st.subheader("Single Stock Deep-Dive & Risk Management")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_symbol = st.text_input("Enter NSE Ticker (e.g. RELIANCE, TATAMOTORS, INFY):", value="RELIANCE").upper().strip()
    with col2:
        period_choice = st.selectbox("Timeframe:", ["1mo", "3mo", "6mo", "1y"], index=1)
        
    symbol_formatted = f"{user_symbol}.NS" if not user_symbol.endswith(".NS") else user_symbol

    if st.button("Run Quant Analysis"):
        with st.spinner(f"Computing indicators and volatility for {user_symbol}..."):
            try:
                stock = yf.Ticker(symbol_formatted)
                df = stock.history(period=period_choice)
                
                if not df.empty and len(df) >= 14:
                    # Indicators
                    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                    
                    # RSI
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
                    
                    # ATR (Average True Range for Risk/Stop-Loss)
                    df['TR'] = pd.concat([
                        df['High'] - df['Low'],
                        abs(df['High'] - df['Close'].shift(1)),
                        abs(df['Low'] - df['Close'].shift(1))
                    ], axis=1).max(axis=1)
                    df['ATR'] = df['TR'].rolling(window=14).mean()
                    
                    latest = df.iloc[-1]
                    price = latest['Close']
                    rsi = latest['RSI']
                    ema9 = latest['EMA_9']
                    ema21 = latest['EMA_21']
                    atr = latest['ATR']
                    
                    # Metrics Display
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Current Price", f"₹{price:.2f}")
                    m2.metric("RSI (14)", f"{rsi:.1f}")
                    m3.metric("ATR (Volatility)", f"₹{atr:.2f}")
                    m4.metric("Trend", "Bullish 🟢" if ema9 > ema21 else "Bearish 🔴")
                    
                    # Risk & Stop Loss Box
                    st.divider()
                    st.markdown("### 🛡️ AI Risk & Position Sizing Calculator")
                    rc1, rc2 = st.columns(2)
                    
                    suggested_stop_loss = price - (1.5 * atr)
                    suggested_target = price + (2.5 * atr)
                    
                    with rc1:
                        st.error(f"🔴 **Suggested Stop-Loss**: ₹{suggested_stop_loss:.2f} *(Based on 1.5x ATR volatility buffer)*")
                    with rc2:
                        st.success(f"🟢 **Suggested Target Price**: ₹{suggested_target:.2f} *(Risk-to-Reward ~1:1.6)*")
                        
                    st.line_chart(df[['Close', 'EMA_9', 'EMA_21']])
                else:
                    st.error("Invalid symbol or insufficient data.")
            except Exception as e:
                st.error("Failed to fetch market data.")

# --- TAB 2: MULTI-STOCK COMPARISON MATRIX ---
with tab2:
    st.subheader("⚔️ Head-to-Head Stock Battle")
    st.write("Compare multiple NSE stocks side-by-side to find the absolute strongest momentum.")
    
    default_tickers = "RELIANCE, TCS, INFY, TATAMOTORS"
    input_tickers = st.text_input("Enter comma-separated tickers:", value=default_tickers).upper()
    
    if st.button("Compare Stocks"):
        ticker_list = [t.strip() + ".NS" if not t.strip().endswith(".NS") else t.strip() for t in input_tickers.split(",")]
        comparison_data = []
        
        with st.spinner("Analyzing comparative metrics..."):
            for t in ticker_list:
                try:
                    df = yf.Ticker(t).history(period="1mo")
                    if len(df) >= 14:
                        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rsi = 100 - (100 / (1 + (gain / loss)))
                        
                        comparison_data.append({
                            "Ticker": t.replace(".NS", ""),
                            "Price (₹)": round(df['Close'].iloc[-1], 2),
                            "RSI": round(rsi.iloc[-1], 1),
                            "Trend": "Bullish 📈" if df['EMA_9'].iloc[-1] > df['EMA_21'].iloc[-1] else "Bearish 📉",
                            "1M Return (%)": round(((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100, 2)
                        })
                except:
                    pass
                    
            if comparison_data:
                comp_df = pd.DataFrame(comparison_data)
                st.dataframe(comp_df.sort_values(by="1M Return (%)", ascending=False), use_container_width=True)
            else:
                st.warning("No valid data retrieved for comparison.")

# --- TAB 3: MARKET BREADTH & SENTIMENT METER ---
with tab3:
    st.subheader("📊 Live NSE Market Sentiment Breadth")
    st.write("Scans major index heavyweights to calculate overall market bullish/bearish pressure.")
    
    if st.button("Calculate Market Sentiment"):
        sentiment_watchlist = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "TATAMOTORS.NS", "INFY.NS", "ITC.NS", "ICICIBANK.NS", "LT.NS"]
        advancing = 0
        declining = 0
        
        with st.spinner("Analyzing market breadth across heavyweights..."):
            for t in sentiment_watchlist:
                try:
                    df = yf.Ticker(t).history(period="5d")
                    if len(df) >= 2:
                        if df['Close'].iloc[-1] > df['Close'].iloc[-2]:
                            advancing += 1
                        else:
                            declining += 1
                except:
                    pass
                    
            total = advancing + declining
            if total > 0:
                bullish_pct = (advancing / total) * 100
                
                m1, m2 = st.columns(2)
                m1.metric("Advancing Heavyweights", f"{advancing} / {total}")
                m2.metric("Market Sentiment Score", f"{bullish_pct:.1f}% Bullish")
                
                st.progress(int(bullish_pct))
                
                if bullish_pct >= 60:
                    st.success("🟢 **Overall Market Sentiment: STRONG BULLISH** — Majority of heavyweights are showing positive momentum.")
                elif bullish_pct <= 40:
                    st.error("🔴 **Overall Market Sentiment: BEARISH / DEFENSIVE** — Selling pressure dominates large caps.")
                else:
                    st.warning("🟡 **Overall Market Sentiment: NEUTRAL / CHOPPY** — Mixed signals across sectors.")

# --- TAB 4: IPO TRACKER ---
with tab4:
    st.subheader("🚀 Live & Upcoming Mainboard IPOs")
    ipo_data = [
        {"Company": "Fusion CX", "Type": "Mainboard", "Price Band": "₹275 - ₹289", "Dates": "Oct 14 - Oct 16, 2026", "Status": "Open Now"},
        {"Company": "Tonbo Imaging India", "Type": "Mainboard", "Price Band": "₹665 - ₹700", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Zetwerk Manufacturing", "Type": "Mainboard", "Price Band": "₹143 - ₹151", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Reliance Jio Platforms", "Type": "Mainboard", "Price Band": "TBA", "Dates": "Expected 2026", "Status": "Filing Stage"}
    ]
    st.dataframe(pd.DataFrame(ipo_data), use_container_width=True)

# --- TAB 5: KNOWLEDGE HUB ---
with tab5:
    st.subheader("📚 Quant Terminal Guide")
    st.markdown("""
    * **ATR (Average True Range)**: Measures volatility. Used to place logical stop-losses so your trade doesn't get shaken out by normal market noise.
    * **Market Breadth**: Tells you whether the entire market is pushing up together or if only a few stocks are moving.
    """)import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="AI Quant Terminal", page_icon="⚡", layout="wide")

st.title("⚡ AI Quant Terminal & Market Command Center")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Quant Analysis & Risk", 
    "⚔️ Stock Comparison Matrix", 
    "📊 Market Sentiment Meter", 
    "🚀 Live IPOs", 
    "📚 Knowledge Hub"
])

# --- TAB 1: QUANT ANALYSIS & RISK CALCULATOR ---
with tab1:
    st.subheader("Single Stock Deep-Dive & Risk Management")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_symbol = st.text_input("Enter NSE Ticker (e.g. RELIANCE, TATAMOTORS, INFY):", value="RELIANCE").upper().strip()
    with col2:
        period_choice = st.selectbox("Timeframe:", ["1mo", "3mo", "6mo", "1y"], index=1)
        
    symbol_formatted = f"{user_symbol}.NS" if not user_symbol.endswith(".NS") else user_symbol

    if st.button("Run Quant Analysis"):
        with st.spinner(f"Computing indicators and volatility for {user_symbol}..."):
            try:
                stock = yf.Ticker(symbol_formatted)
                df = stock.history(period=period_choice)
                
                if not df.empty and len(df) >= 14:
                    # Indicators
                    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                    
                    # RSI
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
                    
                    # ATR (Average True Range for Risk/Stop-Loss)
                    df['TR'] = pd.concat([
                        df['High'] - df['Low'],
                        abs(df['High'] - df['Close'].shift(1)),
                        abs(df['Low'] - df['Close'].shift(1))
                    ], axis=1).max(axis=1)
                    df['ATR'] = df['TR'].rolling(window=14).mean()
                    
                    latest = df.iloc[-1]
                    price = latest['Close']
                    rsi = latest['RSI']
                    ema9 = latest['EMA_9']
                    ema21 = latest['EMA_21']
                    atr = latest['ATR']
                    
                    # Metrics Display
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Current Price", f"₹{price:.2f}")
                    m2.metric("RSI (14)", f"{rsi:.1f}")
                    m3.metric("ATR (Volatility)", f"₹{atr:.2f}")
                    m4.metric("Trend", "Bullish 🟢" if ema9 > ema21 else "Bearish 🔴")
                    
                    # Risk & Stop Loss Box
                    st.divider()
                    st.markdown("### 🛡️ AI Risk & Position Sizing Calculator")
                    rc1, rc2 = st.columns(2)
                    
                    suggested_stop_loss = price - (1.5 * atr)
                    suggested_target = price + (2.5 * atr)
                    
                    with rc1:
                        st.error(f"🔴 **Suggested Stop-Loss**: ₹{suggested_stop_loss:.2f} *(Based on 1.5x ATR volatility buffer)*")
                    with rc2:
                        st.success(f"🟢 **Suggested Target Price**: ₹{suggested_target:.2f} *(Risk-to-Reward ~1:1.6)*")
                        
                    st.line_chart(df[['Close', 'EMA_9', 'EMA_21']])
                else:
                    st.error("Invalid symbol or insufficient data.")
            except Exception as e:
                st.error("Failed to fetch market data.")

# --- TAB 2: MULTI-STOCK COMPARISON MATRIX ---
with tab2:
    st.subheader("⚔️ Head-to-Head Stock Battle")
    st.write("Compare multiple NSE stocks side-by-side to find the absolute strongest momentum.")
    
    default_tickers = "RELIANCE, TCS, INFY, TATAMOTORS"
    input_tickers = st.text_input("Enter comma-separated tickers:", value=default_tickers).upper()
    
    if st.button("Compare Stocks"):
        ticker_list = [t.strip() + ".NS" if not t.strip().endswith(".NS") else t.strip() for t in input_tickers.split(",")]
        comparison_data = []
        
        with st.spinner("Analyzing comparative metrics..."):
            for t in ticker_list:
                try:
                    df = yf.Ticker(t).history(period="1mo")
                    if len(df) >= 14:
                        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rsi = 100 - (100 / (1 + (gain / loss)))
                        
                        comparison_data.append({
                            "Ticker": t.replace(".NS", ""),
                            "Price (₹)": round(df['Close'].iloc[-1], 2),
                            "RSI": round(rsi.iloc[-1], 1),
                            "Trend": "Bullish 📈" if df['EMA_9'].iloc[-1] > df['EMA_21'].iloc[-1] else "Bearish 📉",
                            "1M Return (%)": round(((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100, 2)
                        })
                except:
                    pass
                    
            if comparison_data:
                comp_df = pd.DataFrame(comparison_data)
                st.dataframe(comp_df.sort_values(by="1M Return (%)", ascending=False), use_container_width=True)
            else:
                st.warning("No valid data retrieved for comparison.")

# --- TAB 3: MARKET BREADTH & SENTIMENT METER ---
with tab3:
    st.subheader("📊 Live NSE Market Sentiment Breadth")
    st.write("Scans major index heavyweights to calculate overall market bullish/bearish pressure.")
    
    if st.button("Calculate Market Sentiment"):
        sentiment_watchlist = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "TATAMOTORS.NS", "INFY.NS", "ITC.NS", "ICICIBANK.NS", "LT.NS"]
        advancing = 0
        declining = 0
        
        with st.spinner("Analyzing market breadth across heavyweights..."):
            for t in sentiment_watchlist:
                try:
                    df = yf.Ticker(t).history(period="5d")
                    if len(df) >= 2:
                        if df['Close'].iloc[-1] > df['Close'].iloc[-2]:
                            advancing += 1
                        else:
                            declining += 1
                except:
                    pass
                    
            total = advancing + declining
            if total > 0:
                bullish_pct = (advancing / total) * 100
                
                m1, m2 = st.columns(2)
                m1.metric("Advancing Heavyweights", f"{advancing} / {total}")
                m2.metric("Market Sentiment Score", f"{bullish_pct:.1f}% Bullish")
                
                st.progress(int(bullish_pct))
                
                if bullish_pct >= 60:
                    st.success("🟢 **Overall Market Sentiment: STRONG BULLISH** — Majority of heavyweights are showing positive momentum.")
                elif bullish_pct <= 40:
                    st.error("🔴 **Overall Market Sentiment: BEARISH / DEFENSIVE** — Selling pressure dominates large caps.")
                else:
                    st.warning("🟡 **Overall Market Sentiment: NEUTRAL / CHOPPY** — Mixed signals across sectors.")

# --- TAB 4: IPO TRACKER ---
with tab4:
    st.subheader("🚀 Live & Upcoming Mainboard IPOs")
    ipo_data = [
        {"Company": "Fusion CX", "Type": "Mainboard", "Price Band": "₹275 - ₹289", "Dates": "Oct 14 - Oct 16, 2026", "Status": "Open Now"},
        {"Company": "Tonbo Imaging India", "Type": "Mainboard", "Price Band": "₹665 - ₹700", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Zetwerk Manufacturing", "Type": "Mainboard", "Price Band": "₹143 - ₹151", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Reliance Jio Platforms", "Type": "Mainboard", "Price Band": "TBA", "Dates": "Expected 2026", "Status": "Filing Stage"}
    ]
    st.dataframe(pd.DataFrame(ipo_data), use_container_width=True)

# --- TAB 5: KNOWLEDGE HUB ---
with tab5:
    st.subheader("📚 Quant Terminal Guide")
    st.markdown("""
    * **ATR (Average True Range)**: Measures volatility. Used to place logical stop-losses so your trade doesn't get shaken out by normal market noise.
    * **Market Breadth**: Tells you whether the entire market is pushing up together or if only a few stocks are moving.
    """)
