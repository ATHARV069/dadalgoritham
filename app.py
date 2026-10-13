import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="AI Market Command Center", page_icon="🤖", layout="wide")

st.title("🤖 AI Market Command Center & Trading Assistant")

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Stock Search & AI Analysis", "🏆 AI Stock Screener", "🚀 Live & Upcoming IPOs", "📚 Market Knowledge Hub"])

# --- TAB 1: ANY STOCK SEARCH ---
with tab1:
    st.subheader("Search & Analyze Any Indian Stock")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_symbol = st.text_input("Enter NSE Ticker Symbol (e.g. RELIANCE, TATAMOTORS, INFY, ZOMATO):", value="RELIANCE").upper().strip()
    with col2:
        period_choice = st.selectbox("Select Timeframe:", ["1mo", "3mo", "6mo", "1y"], index=1)
        
    symbol_formatted = f"{user_symbol}.NS" if not user_symbol.endswith(".NS") else user_symbol

    if st.button("Run AI Analysis"):
        with st.spinner(f"Analyzing live data for {user_symbol}..."):
            try:
                stock = yf.Ticker(symbol_formatted)
                df = stock.history(period=period_choice)
                
                if not df.empty and len(df) >= 14:
                    # Indicators
                    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                    
                    # RSI Calculation
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    
                    latest = df.iloc[-1]
                    price = latest['Close']
                    rsi = latest['RSI']
                    ema9 = latest['EMA_9']
                    ema21 = latest['EMA_21']
                    
                    # Display Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Current Price", f"₹{price:.2f}")
                    m2.metric("RSI (14-day)", f"{rsi:.1f}")
                    m3.metric("AI Trend Detection", "Uptrend 🟢" if ema9 > ema21 else "Downtrend 🔴")
                    
                    # Signal Decision
                    st.divider()
                    if ema9 > ema21 and rsi < 70:
                        st.success("🟢 **AI Verdict: STRONG BUY SETUP** — Stock shows strong momentum and healthy entry levels.")
                    elif ema9 > ema21 and rsi >= 70:
                        st.warning("⚠️ **AI Verdict: HOLD / OVERBOUGHT** — Uptrend is active, but RSI is high (>70). Wait for a dip.")
                    elif ema9 < ema21 and rsi <= 30:
                        st.info("🔵 **AI Verdict: OVERSOLD WATCH** — Price is dropping, but RSI indicates extreme oversold levels. Watch for a reversal.")
                    else:
                        st.error("🔴 **AI Verdict: BEARISH / AVOID** — Momentum is currently negative.")
                        
                    st.line_chart(df[['Close', 'EMA_9', 'EMA_21']])
                else:
                    st.error("Invalid symbol or not enough trading data available. Try standard NSE symbols like TCS, SBIN, ICICIBANK.")
            except Exception as e:
                st.error("Unable to connect to market service. Please check the stock symbol.")

# --- TAB 2: BEST STOCK FINDER ---
with tab2:
    st.subheader("Automated AI Stock Screener")
    st.write("Scans major NSE heavyweights and ranks them based on technical strength.")
    
    watchlist = {
        "Reliance": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC Bank": "HDFCBANK.NS",
        "Airtel": "BHARTIARTL.NS", "SBI": "SBIN.NS", "Tata Motors": "TATAMOTORS.NS",
        "Infosys": "INFY.NS", "ITC": "ITC.NS", "L&T": "LT.NS", "ICICI Bank": "ICICIBANK.NS"
    }
    
    if st.button("Run Market Scan"):
        results = []
        with st.spinner("AI is evaluating watchlist performance..."):
            for name, ticker in watchlist.items():
                try:
                    df = yf.Ticker(ticker).history(period="1mo")
                    if len(df) >= 14:
                        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rsi = 100 - (100 / (1 + (gain / loss)))
                        
                        latest_price = df['Close'].iloc[-1]
                        latest_rsi = rsi.iloc[-1]
                        is_uptrend = df['EMA_9'].iloc[-1] > df['EMA_21'].iloc[-1]
                        
                        score = "Wait 🟡"
                        if is_uptrend and 40 <= latest_rsi <= 65:
                            score = "Best Buy 🟢"
                        elif is_uptrend and latest_rsi > 65:
                            score = "Overbought ⚠️"
                        elif not is_uptrend and latest_rsi < 30:
                            score = "Oversold Watch 🔵"
                        elif not is_uptrend:
                            score = "Bearish 🔴"
                            
                        results.append({
                            "Stock Name": name,
                            "Price (₹)": round(latest_price, 2),
                            "RSI": round(latest_rsi, 1),
                            "Trend": "Bullish 📈" if is_uptrend else "Bearish 📉",
                            "AI Rating": score
                        })
                except:
                    pass
            
            res_df = pd.DataFrame(results)
            st.dataframe(res_df.sort_values(by="AI Rating"), use_container_width=True)

# --- TAB 3: IPO TRACKER ---
with tab3:
    st.subheader("Current & Upcoming Mainboard IPOs")
    st.info("💡 Keep track of upcoming mainboard issues and filing stages.")
    
    ipo_data = [
        {"Company": "Fusion CX", "Type": "Mainboard", "Price Band": "₹275 - ₹289", "Dates": "Oct 14 - Oct 16, 2026", "Status": "Open Now"},
        {"Company": "Tonbo Imaging India", "Type": "Mainboard", "Price Band": "₹665 - ₹700", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Zetwerk Manufacturing", "Type": "Mainboard", "Price Band": "₹143 - ₹151", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Bonfiglioli Transmissions", "Type": "Mainboard", "Price Band": "₹558 - ₹586", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Sahajanand Medical", "Type": "Mainboard", "Price Band": "₹327 - ₹344", "Dates": "Oct 15 - Oct 19, 2026", "Status": "Upcoming"},
        {"Company": "Reliance Jio Platforms", "Type": "Mainboard", "Price Band": "TBA", "Dates": "Expected 2026", "Status": "Filing Stage"},
        {"Company": "PhonePe", "Type": "Mainboard", "Price Band": "TBA", "Dates": "Expected 2026", "Status": "Filing Stage"}
    ]
    
    st.dataframe(pd.DataFrame(ipo_data), use_container_width=True)

# --- TAB 4: MARKET KNOWLEDGE HUB ---
with tab4:
    st.subheader("📚 AI Indicator Reference Guide")
    
    st.markdown("""
    ### 1. Relative Strength Index (RSI)
    * **Below 30**: Oversold region. Potential reversal/bounce zone.
    * **40 to 65**: Ideal bullish momentum corridor.
    * **Above 70**: Overbought region. High chance of a short-term correction.
    
    ### 2. EMA Crossover Strategy
    * **EMA 9 > EMA 21**: Short-term buyers are in control (Bullish).
    * **EMA 9 < EMA 21**: Sellers dominate the price action (Bearish).
    
    ### 3. High-Probability Setup
    The AI screener flags a **Best Buy** when a stock is in an uptrend (`EMA 9 > EMA 21`) while its RSI remains balanced (`40 to 65`).
    """)
