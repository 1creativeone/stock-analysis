# screener.py
import yfinance as yf
import pandas as pd
from patterns import double_bottom, rsi_divergence, breakout_52w
from backtester import vectorized_backtest
from tqdm import tqdm
import os
from datetime import datetime


# S&P 500 tickers - major companies for demo
# For full list, fetch from: https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
SP500_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "V", "XOM", "WMT", "JPM", "MA", "PG", "CVX", "HD", "LLY", "ABBV",
    "MRK", "AVGO", "PEP", "KO", "COST", "ADBE", "MCD", "TMO", "CSCO", "ACN",
    "ABT", "NFLX", "DHR", "CRM", "VZ", "NKE", "INTC", "TXN", "WFC", "DIS",
    "AMD", "QCOM", "CMCSA", "UPS", "PM", "NEE", "AMGN", "RTX", "HON", "INTU",
    "COP", "IBM", "LOW", "CAT", "SPGI", "BA", "GE", "SBUX", "AMAT", "DE",
    "PLD", "ELV", "GILD", "MDLZ", "ADI", "BKNG", "BLK", "CI", "LMT", "SYK",
    "ADP", "ISRG", "MMC", "TJX", "AMT", "REGN", "VRTX", "ZTS", "CVS", "PGR",
    "C", "TMUS", "MO", "SO", "CB", "DUK", "BDX", "EOG", "SCHW", "BSX",
    "PNC", "HUM", "ITW", "NOC", "ETN", "LRCX", "APD", "MMM", "AON", "ICE",
]


DATA_DIR = "data"
RESULT_DIR = "results"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


def get_sp500_tickers():
    """
    Fetch S&P 500 ticker list from Wikipedia.
    Falls back to hardcoded list if fetch fails.
    """
    try:
        import pandas as pd
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-').tolist()
        print(f"Fetched {len(tickers)} S&P 500 tickers from Wikipedia")
        return tickers
    except Exception as e:
        print(f"Could not fetch S&P 500 list: {e}")
        print(f"Using fallback list of {len(SP500_TICKERS)} major tickers")
        return SP500_TICKERS


def download(ticker, period="10y"):
    """
    Download or load cached stock data.

    Args:
        ticker: Stock symbol
        period: yfinance period (default: 10y)

    Returns:
        DataFrame with OHLCV data
    """
    path = f"{DATA_DIR}/{ticker}.csv"

    # Use cached data if available
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        return df

    # Download new data
    try:
        df = yf.download(ticker, period=period, progress=False)
        if len(df) > 0:
            df.to_csv(path)
        return df
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")
        return pd.DataFrame()


def run_full_scan(tickers=None, top_n=5, min_trades=3):
    """
    Scan all tickers for patterns and backtest them.

    Args:
        tickers: List of ticker symbols (default: fetch S&P 500)
        top_n: Number of top signals to return
        min_trades: Minimum number of trades required

    Returns:
        DataFrame with top signals ranked by Sharpe ratio
    """
    if tickers is None:
        tickers = get_sp500_tickers()

    results = []

    print(f"\nScanning {len(tickers)} tickers...")
    for ticker in tqdm(tickers, desc="Scanning"):
        try:
            df = download(ticker, period="10y")

            # Skip if insufficient data
            if len(df) < 500:
                continue

            # Run all 3 patterns
            patterns = {
                'Double Bottom': double_bottom(df),
                'RSI Divergence': rsi_divergence(df),
                '52W Breakout': breakout_52w(df)
            }

            for name, signal in patterns.items():
                if not signal.any():
                    continue

                # Backtest the pattern
                bt = vectorized_backtest(df, signal)

                # Skip if too few trades or invalid Sharpe
                if bt['num_trades'] < min_trades or pd.isna(bt['sharpe']):
                    continue

                # Store results
                results.append({
                    'ticker': ticker,
                    'pattern': name,
                    'sharpe': bt['sharpe'],
                    'cagr': bt['cagr'],
                    'max_dd': bt['max_dd'],
                    'win_rate': bt['win_rate'],
                    'num_trades': bt['num_trades'],
                    'latest_signal': bt['signal_dates'][-1] if bt['signal_dates'] else None,
                })

        except Exception as e:
            print(f"\nError processing {ticker}: {e}")
            continue

    # Process results
    if len(results) == 0:
        print("\nNo signals found matching criteria.")
        return pd.DataFrame()

    df_res = pd.DataFrame(results)

    # Sort by Sharpe ratio
    df_res = df_res.sort_values('sharpe', ascending=False)

    # Get top N
    top = df_res.head(top_n)

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    top.to_csv(f"{RESULT_DIR}/top_{top_n}.csv", index=False)
    df_res.to_csv(f"{RESULT_DIR}/all_signals_{timestamp}.csv", index=False)

    # Display results
    print(f"\n{'='*80}")
    print(f"TOP {top_n} SIGNALS - Ranked by Sharpe Ratio")
    print(f"{'='*80}\n")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(top[['ticker', 'pattern', 'sharpe', 'cagr', 'max_dd', 'num_trades', 'latest_signal']])

    print(f"\n{'='*80}")
    print(f"Results saved to:")
    print(f"  - {RESULT_DIR}/top_{top_n}.csv")
    print(f"  - {RESULT_DIR}/all_signals_{timestamp}.csv")
    print(f"{'='*80}\n")

    # Plot equity curves for top signals
    try:
        plot_top_equity_curves(top)
    except Exception as e:
        print(f"Could not generate equity plot: {e}")

    return top


def plot_top_equity_curves(top_df):
    """Generate equity curve plot for top signals."""
    import matplotlib.pyplot as plt

    plt.figure(figsize=(14, 8))

    for idx, row in top_df.iterrows():
        try:
            ticker = row['ticker']
            pattern = row['pattern']

            # Load data
            df = pd.read_csv(f"{DATA_DIR}/{ticker}.csv", index_col=0, parse_dates=True)

            # Recreate pattern signal
            if pattern == 'Double Bottom':
                signal = double_bottom(df)
            elif pattern == 'RSI Divergence':
                signal = rsi_divergence(df)
            else:  # 52W Breakout
                signal = breakout_52w(df)

            # Run backtest
            bt = vectorized_backtest(df, signal)

            # Plot equity curve
            plt.plot(bt['equity'].index, bt['equity'],
                    label=f"{ticker} - {pattern} (Sharpe: {row['sharpe']:.2f})",
                    linewidth=2)

        except Exception as e:
            print(f"Could not plot {ticker}: {e}")

    plt.title("Top Pattern Equity Curves (10-Year Backtest)", fontsize=16, fontweight='bold')
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Portfolio Value ($)", fontsize=12)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save plot
    plot_path = f"{RESULT_DIR}/top_equity.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Equity curve saved to: {plot_path}")
    plt.close()


if __name__ == "__main__":
    run_full_scan(top_n=5)
