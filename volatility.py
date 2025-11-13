#!/usr/bin/env python3
# volatility.py
"""
Volatility Analysis Module

Provides comprehensive volatility metrics and analysis tools.
"""
import pandas as pd
import numpy as np


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).

    Args:
        df: DataFrame with OHLC data
        period: ATR period (default: 14)

    Returns:
        ATR values
    """
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(period).mean()

    return atr


def calculate_historical_volatility(df: pd.DataFrame, period: int = 30) -> pd.Series:
    """
    Calculate Historical Volatility (annualized standard deviation of returns).

    Args:
        df: DataFrame with price data
        period: Rolling window period (default: 30)

    Returns:
        Historical volatility (annualized)
    """
    returns = df['Close'].pct_change()
    hist_vol = returns.rolling(period).std() * np.sqrt(252)  # Annualize

    return hist_vol


def calculate_volatility_percentile(df: pd.DataFrame, lookback: int = 252) -> pd.Series:
    """
    Calculate current volatility percentile rank.

    Args:
        df: DataFrame with price data
        lookback: Period for percentile calculation

    Returns:
        Volatility percentile rank (0-100)
    """
    hist_vol = calculate_historical_volatility(df, period=30)

    percentile = pd.Series(index=df.index, dtype=float)

    for i in range(lookback, len(df)):
        window = hist_vol.iloc[i-lookback:i]
        current = hist_vol.iloc[i]

        if pd.notna(current):
            rank = (window < current).sum() / len(window.dropna()) * 100
            percentile.iloc[i] = rank

    return percentile


def get_volatility_metrics(df: pd.DataFrame) -> dict:
    """
    Calculate comprehensive volatility metrics.

    Args:
        df: DataFrame with OHLCV data

    Returns:
        Dictionary with volatility metrics
    """
    # ATR
    atr = calculate_atr(df)
    current_atr = atr.iloc[-1]
    atr_pct = (current_atr / df['Close'].iloc[-1]) * 100

    # Historical Volatility
    hist_vol = calculate_historical_volatility(df, period=30)
    current_hv = hist_vol.iloc[-1]

    # Volatility percentile
    vol_percentile = calculate_volatility_percentile(df)
    current_percentile = vol_percentile.iloc[-1]

    # Price range metrics
    high_low_range = ((df['High'] - df['Low']) / df['Close'] * 100).iloc[-20:].mean()

    # Volatility trend (increasing/decreasing)
    vol_trend = "Increasing" if hist_vol.iloc[-1] > hist_vol.iloc[-30:].mean() else "Decreasing"

    return {
        'atr': current_atr,
        'atr_pct': atr_pct,
        'historical_volatility': current_hv,
        'volatility_percentile': current_percentile,
        'avg_daily_range_pct': high_low_range,
        'volatility_trend': vol_trend,
        'atr_series': atr,
        'hist_vol_series': hist_vol,
        'vol_percentile_series': vol_percentile
    }


def volatility_heatmap_data(tickers: list, data_dir: str = "data") -> pd.DataFrame:
    """
    Generate volatility heatmap data for multiple tickers.

    Args:
        tickers: List of ticker symbols
        data_dir: Directory with cached data

    Returns:
        DataFrame with volatility metrics for each ticker
    """
    import os

    results = []

    for ticker in tickers:
        path = f"{data_dir}/{ticker}.csv"
        if not os.path.exists(path):
            continue

        try:
            df = pd.read_csv(path, index_col=0, parse_dates=True)

            metrics = get_volatility_metrics(df)

            results.append({
                'ticker': ticker,
                'atr_pct': metrics['atr_pct'],
                'hist_vol': metrics['historical_volatility'] * 100,  # As percentage
                'vol_percentile': metrics['volatility_percentile'],
                'daily_range': metrics['avg_daily_range_pct'],
                'trend': metrics['volatility_trend']
            })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    return pd.DataFrame(results)


def classify_volatility(vol_percentile: float) -> str:
    """
    Classify volatility level.

    Args:
        vol_percentile: Volatility percentile (0-100)

    Returns:
        Classification string
    """
    if vol_percentile < 20:
        return "Very Low"
    elif vol_percentile < 40:
        return "Low"
    elif vol_percentile < 60:
        return "Normal"
    elif vol_percentile < 80:
        return "High"
    else:
        return "Very High"


if __name__ == "__main__":
    """Test volatility analysis."""
    print("Testing volatility analysis module...")

    # Generate test data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=500, freq='D')

    # Simulate price with varying volatility
    returns = np.random.randn(500) * 0.02  # 2% daily volatility
    price = 100 * (1 + returns).cumprod()

    df = pd.DataFrame({
        'Open': price * 0.99,
        'High': price * 1.02,
        'Low': price * 0.98,
        'Close': price,
        'Volume': np.random.randint(1_000_000, 10_000_000, 500)
    }, index=dates)

    # Test metrics
    metrics = get_volatility_metrics(df)

    print(f"\n✅ Volatility Metrics:")
    print(f"  ATR: ${metrics['atr']:.2f} ({metrics['atr_pct']:.2f}%)")
    print(f"  Historical Vol: {metrics['historical_volatility']:.2%}")
    print(f"  Vol Percentile: {metrics['volatility_percentile']:.1f}")
    print(f"  Avg Daily Range: {metrics['avg_daily_range_pct']:.2f}%")
    print(f"  Trend: {metrics['volatility_trend']}")
    print(f"  Classification: {classify_volatility(metrics['volatility_percentile'])}")

    print("\n✅ Volatility analysis module working!")
