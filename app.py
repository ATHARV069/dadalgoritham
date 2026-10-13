import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Dad's Stock & IPO Assistant", page_icon="📈", layout="centered")

st.title("📈 Dad's Stock & IPO Assistant")

# Tabs for easy mobile navigation
tab1, tab2 = st.tabs(["🔍 Stock Analysis", "🚀 IPO Tracker"])

# --- TAB 1: STOCK ANALYSIS ---
with tab1:
    st.subheader("Select or Search Stock")
    
    # Popular Nifty 50 & Major Stocks dictionary
    stock_dict = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Bharti Airtel": "BHARTIARTL.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India (SBI)": "SBIN.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Infosys": "INFY.NS",
        "Larsen & Toubro": "LT.NS",
        "Sun Pharma": "SUNPHARMA.NS"
    }
    
    selected_name = st.selectbox("Choose a popular stock:", list(stock_dict.keys()))
    symbol_input = st.text_input("Or enter any NSE Stock Symbol manually (e.g. WIPRO.NS, ITC.NS):", value=stock_dict[selected_name])
    
    if st.button("Analyze Stock Signal"):
        with st.spinner("Fetching data..."):
            try:
                ticker = yf.Ticker(symbol_input)
                df = ticker.history(period="1d", interval="5m")
                
                if not df.empty and len(df) >= 21:
                    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                    
                    latest = df.iloc[-1]
                    price = latest['Close']
                    
                    st.metric(label=f"Current Price ({symbol_input})", value=f"₹{price:.2f}")
                    
                    if latest['EMA_9'] > latest['EMA_21']:
                        st.success("🟢 **Signal: BULLISH / BUY** (Short-term trend is upward)")
                    else:
                        st.error("🔴 **Signal: BEARISH / EXIT** (Short-term trend is downward)")
                        
                    st.line_chart(df['Close'])
                else:
                    st.warning("Insufficient intraday data or market is closed.")
            except Exception as e:
                st.error(f"Error fetching stock data: {e}")

# --- TAB 2: IPO TRACKER ---
with tab2:
    st.subheader("Current & Upcoming Mainboard IPOs")
    st.info("💡 Always check the Grey Market Premium (GMP) and company financials before applying for IPOs.")
    
    # Static snapshot of key upcoming/recent IPOs (Can be linked to web scrapers like Chittorgarh/NSE)
    ipo_data = [
        {"Company": "Reliance Jio Platforms", "Status": "Upcoming", "Issue Size": "~₹31,000 Cr", "Expected Date": "Oct 2026"},
        {"Company": "Avaada Electro", "Status": "Upcoming", "Issue Size": "~₹7,600 Cr", "Expected Date": "Oct 2026"},
        {"Company": "Carlsberg India", "Status": "Upcoming", "Issue Size": "~₹6,500 Cr", "Expected Date": "Oct 2026"},
        {"Company": "Vishal Nirmiti", "Status": "Closed/Listing", "Issue Size": "₹178 Cr", "Expected Date": "Oct 2026"},
        {"Company": "Nityas Gems & Jewellery", "Status": "Closed/Listing", "Issue Size": "₹108 Cr", "Expected Date": "Oct 2026"}
    ]
    
    df_ipo = pd.DataFrame(ipo_data)
    st.dataframe(df_ipo, use_container_width=True)