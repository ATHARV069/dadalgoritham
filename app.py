import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Dad's Market Command Center", page_icon="📈", layout="wide")

st.title("📈 Dad's Market Command Center")

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Stock Search & Analysis", "🏆 Best Stock Finder", "🚀 Live & Upcoming IPOs", "📚 Learn & Guides"])

# --- TAB 1: ANY STOCK SEARCH ---
with tab1:
    st.subheader("Search & Analyze Any Indian Stock")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_symbol = st.text_input("Enter NSE Ticker Symbol (e.g. RELIANCE, TATAMOTORS, INFY, ZOMATO):", value="RELIANCE").upper().strip()
    with col2:
        period_choice = st.selectbox("Select Timeframe:", ["1mo", "3mo", "6mo", "1y"], index=1)
        
    symbol_formatted = f"{user_symbol}.NS" if not user_symbol.endswith(".NS") else user_symbol

    if st.button("Fetch Live Stock Analysis"):
        with st.spinner(f"Loading live data for {user_symbol}..."):
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
                    m3.metric("Trend", "Uptrend 🟢" if ema9 > ema21 else "Downtrend 🔴")
                    
                    # Signal Decision
                    st.divider()
                    if ema9 > ema21 and rsi < 70:
                        st.success("🟢 **STRONG BUY SIGNAL**: Stock is in an uptrend and not overbought.")
                    elif ema9 > ema21 and rsi >= 70:
                        st.warning("⚠️ **HOLD / CAUTION**: Stock is in an uptrend, but RSI is overbought (>70). Avoid new buying right now.")
                    elif ema9 < ema21 and rsi <= 30:
                        st.info("🔵 **OVERSOLD WATCHLIST**: Stock is down, but RSI is oversold (<30). Potential bounce candidate.")
                    else:
                        st.error("🔴 **BEARISH / EXIT**: Stock is currently in a downtrend.")
                        
                    st.line_chart(df[['Close', 'EMA_9', 'EMA_21']])
                else:
                    st.error("Invalid symbol or not enough trading data available. Try standard NSE symbols like TCS, SBIN, ICICIBANK.")
            except Exception as e:
                st.error("Unable to connect to market service. Please check the stock symbol.")

# --- TAB 2: BEST STOCK FINDER ---
with tab2:
    st.subheader("Automated Screener: Ranking Popular Stocks")
    st.write("Analyzes a list of major stocks and ranks the best buy opportunities automatically.")
    
    watchlist = {
        "Reliance": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC Bank": "HDFCBANK.NS",
        "Airtel": "BHARTIARTL.NS", "SBI": "SBIN.NS", "Tata Motors": "TATAMOTORS.NS",
        "Infosys": "INFY.NS", "ITC": "ITC.NS", "L&T": "LT.NS", "ICICI Bank": "ICICIBANK.NS"
    }
    
    if st.button("Run Screener Now"):
        results = []
        with st.spinner("Scanning market trends..."):
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
                            "Recommendation": score
                        })
                except:
                    pass
            
            res_df = pd.DataFrame(results)
            st.dataframe(res_df.sort_values(by="Recommendation"), use_container_width=True)

# --- TAB 3: IPO TRACKER ---
with tab3:
    st.subheader("Current & Upcoming Mainboard IPOs")
    st.info("💡 Tip: Prioritize Mainboard IPOs with strong institutional demand and subscription history.")
    
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

# --- TAB 4: LEARN & GUIDES ---
with tab4:
    st.subheader("📚 Quick Stock Learning Guide for Dad")
    
    st.markdown("""
    ### 1. What is RSI (Relative Strength Index)?
    * **RSI Below 30**: Stock is underpriced (oversold). Good area to watch for buying opportunities.
    * **RSI 40 to 65**: Healthy momentum range for riding an upward trend.
    * **RSI Above 70**: Stock is overheated (overbought). High risk of temporary pullback.
    
    ### 2. What is EMA Crossover (Moving Averages)?
    * **EMA 9 > EMA 21 (Green Signal)**: Short-term price momentum is stronger than medium-term momentum. Indicates a **Bullish Trend**.
    * **EMA 9 < EMA 21 (Red Signal)**: Indicates price momentum is dropping. Indicates a **Bearish Trend**.
    
    ### 3. Golden Rule for Buying
    Look for stocks where **EMA 9 is above EMA 21** AND **RSI is between 40 and 65**. This combination offers high-probability setups!
    """)
