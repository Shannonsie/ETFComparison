# 📊 ETF Comparison Platform

A modern Streamlit web app to compare historical performance, risk, and top holdings of any two ETFs using *robust, multi-source data*.

---

## 🚀 Features

- **Compare any two ETFs** by ticker (e.g., `SPY` vs `VOO`)
- **Visualize performance**: normalized returns, rolling correlation, and daily returns scatterplot
- **View key stats**: total return, annualized volatility, correlation, and return difference
- **Get top ETF holdings** from multiple independent sources (see below)
- **See ETF details**: expense ratio, yield, AUM, provider
- **Automatic fallback**: If one holdings source fails or is out of date, the app tries others
- **Official links**: Direct links to ETF provider pages for manual verification

---

## 🛠️ Data Sources

| Data Type      | Source(s) Used                                                                                          |
| -------------- | -----------------------------------------------------------------------------------------------------  |
| **Price & Stats** | [Yahoo Finance](https://finance.yahoo.com/) via [`yfinance`](https://pypi.org/project/yfinance/)       |
| **ETF Holdings** | Tries, in order: [StockAnalysis.com](https://stockanalysis.com/etf/), [Zacks.com](https://zacks.com/funds/etf/), [Yahoo Finance](https://finance.yahoo.com/), [ETFdb.com](https://etfdb.com/), [ETF.com](https://etf.com/) |
| **ETF Facts**    | [Yahoo Finance](https://finance.yahoo.com/) via `yfinance`                                            |

*If all holdings scrapers fail, the app gives you an official link for manual review.*

---

## 📦 Installation & Usage

1. **Clone the repository**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. **Install dependencies**
    ```bash
    pip install streamlit yfinance pandas matplotlib seaborn requests beautifulsoup4
    ```

3. **Run the app**
    ```bash
    streamlit run etf_compare_app.py
    ```

---

## 🖥️ How to Use

1. Enter two ETF tickers in the sidebar (e.g., `SPY`, `VOO`, `QQQ`, `IVV`)
2. Choose your date range for performance comparison
3. View:
    - **Performance charts**
    - **Key statistics**
    - **ETF details**
    - **Top holdings** (from multiple live sources)
4. Click the *official holdings link* if detailed breakdown is not available

---

## 📝 Notes & Disclaimer

- **Web-scraped holdings data** may be unavailable or stale if sources change their layout or block scraping.
- **Always verify ETF holdings** with the official provider link supplied in the app.
- This app is for educational and research purposes only.

---

## 🤝 Contributing

Pull requests and feature ideas are welcome! Please open an issue to discuss changes or new features.

---
