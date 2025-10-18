import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup

# ==================== STREAMLIT APP SETUP ====================
st.set_page_config(page_title="ETF Comparison Tool", layout="centered")

st.title("📊 ETF Comparison Platform")
st.write(
    "Compare the historical performance, correlation, and basic statistics of any two ETFs. "
    "Enter their tickers on the side (e.g., SPY, VOO, QQQ, IVV)."
)

st.sidebar.header("Select ETFs to Compare")
etf1 = st.sidebar.text_input("ETF 1 Ticker", value="SPY").upper()
etf2 = st.sidebar.text_input("ETF 2 Ticker", value="VOO").upper()
today = pd.to_datetime("today").date()
date_range = st.sidebar.date_input(
    "Select date range",
    value=(today - pd.Timedelta(days=90), today)
)

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    st.error("Please select both start and end dates.")
    st.stop()

# ==================== WEB SCRAPING FUNCTIONS ====================

def scrape_zacks(ticker):
    """Scrape holdings from Zacks.com"""
    try:
        url = f"https://www.zacks.com/funds/etf/{ticker}/holding"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            tables = pd.read_html(response.content)
            
            for table in tables:
                if len(table) > 5:
                    cols_str = ' '.join(str(table.columns).lower())
                    if any(keyword in cols_str for keyword in ['symbol', 'holding', 'ticker', 'name']):
                        df = table.copy()
                        df = df[~df.astype(str).apply(lambda x: x.str.contains('total|as of|note:', case=False, na=False)).any(axis=1)]
                        if len(df) >= 5:
                            return df.head(15)
        
        return None
    except Exception as e:
        return None


def scrape_yahoo_holdings(ticker):
    """Scrape holdings from Yahoo Finance"""
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}/holdings"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://finance.yahoo.com/',
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find tables
            tables = pd.read_html(response.content)
            
            for table in tables:
                if len(table) >= 5:
                    cols = [str(c).lower() for c in table.columns]
                    
                    if any(keyword in ' '.join(cols) for keyword in ['symbol', 'holding', 'name', 'ticker']):
                        df = table.copy()
                        df = df[~df.astype(str).apply(lambda x: x.str.contains('total|as of date|other', case=False, na=False)).any(axis=1)]
                        
                        if len(df) >= 5:
                            return df.head(15)
            
            # Method 2: Look for specific div/section with holdings
            holdings_section = soup.find('section', {'data-test': 'holdings'})
            if holdings_section:
                table_html = holdings_section.find('table')
                if table_html:
                    df = pd.read_html(str(table_html))[0]
                    return df.head(15)
        
        return None
    except Exception as e:
        return None


def scrape_etfdb(ticker):
    """Scrape holdings from etfdb.com"""
    try:
        url = f"https://etfdb.com/etf/{ticker}/#holdings"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = pd.read_html(response.content)
            
            for table in tables:
                if len(table) >= 5:
                    cols_str = ' '.join([str(c).lower() for c in table.columns])
                    
                    if 'symbol' in cols_str or 'holding' in cols_str:
                        df = table.copy()
                        df = df[~df.astype(str).apply(lambda x: x.str.contains('total', case=False, na=False)).any(axis=1)]
                        
                        if len(df) >= 5:
                            return df.head(15)
        
        return None
    except Exception as e:
        return None


def scrape_stockanalysis(ticker):
    """Scrape from stockanalysis.com"""
    try:
        url = f"https://stockanalysis.com/etf/{ticker}/holdings/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            tables = pd.read_html(response.content)
            
            for table in tables:
                if len(table) >= 5:
                    return table.head(15)
        
        return None
    except Exception as e:
        return None


def scrape_etfcom(ticker):
    """Scrape holdings from etf.com"""
    try:
        url = f"https://www.etf.com/{ticker}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            tables = pd.read_html(response.content)
            
            for idx, table in enumerate(tables):
                if len(table) >= 5 and len(table.columns) >= 2:
                    first_col_sample = str(table.iloc[:3, 0].values).lower()
                    if any(keyword in first_col_sample for keyword in ['ticker', 'symbol', 'stock', 'holding']):
                        df = table.copy()
                        df = df[~df.astype(str).apply(lambda x: x.str.contains('total|as of', case=False, na=False)).any(axis=1)]
                        
                        if len(df) >= 5:
                            return df.head(15)
        
        return None
    except Exception as e:
        return None


def get_etf_holdings(ticker):
    """
    Try multiple sources to get ETF holdings with detailed feedback
    Returns: (holdings_df, source_name, error_message)
    """
    
    sources = [
        ("Stock Analysis", scrape_stockanalysis),
        ("Zacks", scrape_zacks),
        ("Yahoo Finance", scrape_yahoo_holdings),
        ("ETFDB", scrape_etfdb),
        ("ETF.com", scrape_etfcom),
    ]
    
    errors = []
    
    for source_name, scrape_func in sources:
        try:
            holdings = scrape_func(ticker)
            if holdings is not None and not holdings.empty and len(holdings) >= 5:
                return holdings, source_name, None
        except Exception as e:
            errors.append(f"{source_name}: {str(e)[:50]}")
            continue
    
    # If all sources failed
    error_msg = " | ".join(errors) if errors else "All sources failed"
    return None, None, error_msg


# ==================== HELPER FUNCTIONS ====================

def download_etf_data(tickers, start, end):
    """Download and clean ETF price data."""
    try:
        raw = yf.download(tickers, start=start, end=end, progress=False)
        
        if raw.empty:
            return None
        
        if isinstance(raw.columns, pd.MultiIndex):
            if 'Adj Close' in raw.columns.get_level_values(0):
                data = raw['Adj Close']
            elif 'Close' in raw.columns.get_level_values(0):
                data = raw['Close']
            else:
                data = raw
        else:
            data = raw
        
        if isinstance(data, pd.Series):
            data = data.to_frame()
        
        data.columns = data.columns.astype(str)
        
        return data
    
    except Exception as e:
        st.error(f"Failed to download data: {e}")
        return None


def get_etf_info(ticker):
    """Get ETF information."""
    try:
        etf = yf.Ticker(ticker)
        info = etf.info
        return info
    except Exception as e:
        return {}


def get_holdings_url(ticker, info):
    """Generate URL to view holdings on provider website."""
    provider = (info.get("fundFamily") or "").lower()
    long_name = (info.get("longName") or "").lower()
    
    if "vanguard" in provider or "vanguard" in long_name:
        return f"https://investor.vanguard.com/investment-products/etfs/profile/{ticker}#portfolio-composition"
    elif "ishares" in provider or "blackrock" in provider or "ishares" in long_name:
        return f"https://www.ishares.com/us/products/etf-investments#!type=ishares&view=keyFacts&fac=43511&query={ticker}"
    elif "state street" in provider or "spdr" in provider or "spdr" in long_name:
        return f"https://www.ssga.com/us/en/intermediary/etfs/funds/{ticker.lower()}"
    elif "invesco" in provider or "invesco" in long_name:
        return f"https://www.invesco.com/us/financial-products/etfs/holdings?audienceType=Investor&ticker={ticker}"
    else:
        return f"https://finance.yahoo.com/quote/{ticker}/holdings"


def calculate_statistics(data, ticker1, ticker2):
    """Calculate performance statistics."""
    returns = data.pct_change().dropna()
    
    correlation = returns[ticker1].corr(returns[ticker2])
    vol1 = returns[ticker1].std() * (252 ** 0.5)
    vol2 = returns[ticker2].std() * (252 ** 0.5)
    
    cumulative_return1 = (data[ticker1].iloc[-1] / data[ticker1].iloc[0] - 1)
    cumulative_return2 = (data[ticker2].iloc[-1] / data[ticker2].iloc[0] - 1)
    
    return {
        'correlation': correlation,
        'vol1': vol1,
        'vol2': vol2,
        'cum_return1': cumulative_return1,
        'cum_return2': cumulative_return2,
        'returns': returns
    }


# ==================== MAIN APPLICATION ====================

if etf1 and etf2 and etf1 != etf2:
    with st.spinner("Downloading price data..."):
        data = download_etf_data([etf1, etf2], start_date, end_date)
    
    if data is None or data.empty or etf1 not in data.columns or etf2 not in data.columns:
        st.error("Could not retrieve price data for both tickers. Please check the tickers and date range.")
        st.stop()
    
    data = data[[etf1, etf2]].dropna()
    
    if len(data) < 2:
        st.error("Insufficient data for the selected date range.")
        st.stop()
    
    stats = calculate_statistics(data, etf1, etf2)
    
    # 1. Normalized Price Performance
    st.subheader("📈 Normalized Price Performance")
    normalized_data = data / data.iloc[0] * 100
    
    fig, ax = plt.subplots(figsize=(10, 5))
    normalized_data.plot(ax=ax, linewidth=2)
    ax.set_ylabel("Normalized Price (100 = Start)")
    ax.set_xlabel("Date")
    ax.set_title(f"{etf1} vs {etf2} Performance")
    ax.legend([etf1, etf2])
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close()
    
    # 2. Key Statistics
    st.subheader("📊 Key Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"{etf1} Total Return", f"{stats['cum_return1']:.2%}")
        st.metric(f"{etf1} Volatility", f"{stats['vol1']:.2%}")
    
    with col2:
        st.metric(f"{etf2} Total Return", f"{stats['cum_return2']:.2%}")
        st.metric(f"{etf2} Volatility", f"{stats['vol2']:.2%}")
    
    with col3:
        st.metric("Correlation", f"{stats['correlation']:.4f}")
        st.metric("Return Difference", f"{(stats['cum_return1'] - stats['cum_return2']):.2%}")
    
    # 3. Rolling Correlation
    st.subheader("🔄 60-Day Rolling Correlation")
    rolling_corr = stats['returns'][etf1].rolling(60).corr(stats['returns'][etf2])
    
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    rolling_corr.plot(ax=ax2, color="purple", linewidth=2)
    ax2.set_ylabel("Correlation")
    ax2.set_xlabel("Date")
    ax2.set_title(f"60-Day Rolling Correlation: {etf1} vs {etf2}")
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    st.pyplot(fig2)
    plt.close()
    
    # 4. Daily Returns Scatterplot
    st.subheader("📉 Daily Returns Comparison")
    fig3, ax3 = plt.subplots(figsize=(8, 8))
    sns.scatterplot(x=stats['returns'][etf1], y=stats['returns'][etf2], alpha=0.5, ax=ax3)
    ax3.set_xlabel(f"{etf1} Daily Return")
    ax3.set_ylabel(f"{etf2} Daily Return")
    ax3.set_title("Daily Returns Scatterplot")
    ax3.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    ax3.axvline(x=0, color='black', linestyle='--', alpha=0.3)
    ax3.grid(True, alpha=0.3)
    st.pyplot(fig3)
    plt.close()
    
    # 5. ETF Information
    st.subheader("ℹ️ ETF Information")
    
    info1 = get_etf_info(etf1)
    info2 = get_etf_info(etf2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{etf1}** - {info1.get('longName', 'N/A')}")
        st.write(f"💰 Expense Ratio: {info1.get('expenseRatio', 'N/A')}")
        st.write(f"📈 Yield: {info1.get('yield', info1.get('dividendYield', 'N/A'))}")
        if info1.get('totalAssets'):
            st.write(f"💵 AUM: ${info1.get('totalAssets'):,.0f}")
        else:
            st.write("💵 AUM: N/A")
    
    with col2:
        st.write(f"**{etf2}** - {info2.get('longName', 'N/A')}")
        st.write(f"💰 Expense Ratio: {info2.get('expenseRatio', 'N/A')}")
        st.write(f"📈 Yield: {info2.get('yield', info2.get('dividendYield', 'N/A'))}")
        if info2.get('totalAssets'):
            st.write(f"💵 AUM: ${info2.get('totalAssets'):,.0f}")
        else:
            st.write("💵 AUM: N/A")
    
    # 6. Holdings (Web Scraped)
    st.subheader("📋 Top Holdings")
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{etf1} Holdings**")
        with st.spinner(f"Fetching {etf1} holdings..."):
            holdings1, source1, error1 = get_etf_holdings(etf1)
        
        if holdings1 is not None and not holdings1.empty:
            st.success(f"✓ Source: {source1}")
            st.dataframe(holdings1, use_container_width=True, height=400)
        else:
            st.warning(f"⚠️ Unable to fetch holdings for {etf1}")
            with st.expander("Show error details"):
                st.caption(error1 if error1 else "No specific error")
            st.markdown(f"[📊 View official holdings]({get_holdings_url(etf1, info1)})")
    
    with col2:
        st.write(f"**{etf2} Holdings**")
        with st.spinner(f"Fetching {etf2} holdings..."):
            holdings2, source2, error2 = get_etf_holdings(etf2)
        
        if holdings2 is not None and not holdings2.empty:
            st.success(f"✓ Source: {source2}")
            st.dataframe(holdings2, use_container_width=True, height=400)
        else:
            st.warning(f"⚠️ Unable to fetch holdings for {etf2}")
            with st.expander("Show error details"):
                st.caption(error2 if error2 else "No specific error")
            st.markdown(f"[📊 View official holdings]({get_holdings_url(etf2, info2)})")

else:
    st.info("👆 Enter two different ETF tickers in the sidebar to begin comparison.")

st.markdown("---")
st.caption("Built with Streamlit, yfinance, pandas, and matplotlib")
st.caption("⚠️ Disclaimer: Web-scraped holdings data may be delayed or incomplete. Always verify with official sources.")