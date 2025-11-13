# patterns.py
import pandas as pd
import numpy as np


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index).

    Args:
        series: Price series
        period: RSI period (default: 14)

    Returns:
        RSI values
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def double_bottom(df: pd.DataFrame, window=20, tol=0.03) -> pd.Series:
    """
    Detect Double Bottom pattern with breakout confirmation.

    Returns boolean Series: True on the bar where the pattern completes.

    Rules:
    - Two troughs within 2*window periods
    - Troughs within ±tol% of each other
    - Peak between the troughs
    - Breakout above peak confirms the pattern
    """
    low = df['Low'].rolling(window).min()
    signals = pd.Series(False, index=df.index)

    for i in range(window*2, len(df)):
        recent = df.iloc[i-2*window:i]
        lows = recent['Low'][recent['Low'] == recent['Low'].min()]

        if len(lows) >= 2:
            p1, p2 = lows.index[0], lows.index[-1]
            peak = df['High'].loc[p1:p2].max()

            # Check if current low is similar to previous lows
            if abs(df['Low'].iloc[i] - lows.mean()) < tol * lows.mean():
                # Breakout confirms the pattern
                if df['Close'].iloc[i] > peak:
                    signals.iloc[i] = True

    return signals


def rsi_divergence(df: pd.DataFrame, period=14, lookback=30) -> pd.Series:
    """
    Detect RSI Bullish Divergence.

    Returns boolean Series: True when divergence is detected.

    Rules:
    - Price makes a lower low
    - RSI makes a higher low (bullish divergence)
    - Lookback period to compare lows
    """
    df = df.copy()
    df['RSI'] = calculate_rsi(df['Close'], period=period)
    signals = pd.Series(False, index=df.index)

    for i in range(lookback, len(df)):
        price = df['Low'].iloc[i-lookback:i]
        rsi_val = df['RSI'].iloc[i-lookback:i]

        # Price lower low, RSI higher low = bullish divergence
        if price.min() < price.iloc[:-5].min() and rsi_val.min() > rsi_val.iloc[:-5].min():
            signals.iloc[i] = True

    return signals


def breakout_52w(df: pd.DataFrame) -> pd.Series:
    """
    Detect 52-Week High Breakout.

    Returns boolean Series: True when close exceeds 52-week high.

    Rules:
    - Close price breaks above the highest high of past 252 days (1 year)
    - Uses shift(1) to avoid look-ahead bias
    """
    high_52w = df['High'].rolling(252).max().shift(1)
    return df['Close'] > high_52w


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).

    Args:
        series: Price series
        period: EMA period

    Returns:
        EMA values
    """
    return series.ewm(span=period, adjust=False).mean()


def ema_crossover(df: pd.DataFrame, fast_period=12, slow_period=26, volume_filter=True) -> pd.Series:
    """
    Detect EMA Crossover (Golden Cross).

    Returns boolean Series: True when fast EMA crosses above slow EMA.

    Rules:
    - Fast EMA (default: 12) crosses above slow EMA (default: 26)
    - Optional volume filter: volume > 20-day average
    - Uses shift(1) to avoid look-ahead bias
    """
    fast_ema = calculate_ema(df['Close'], fast_period)
    slow_ema = calculate_ema(df['Close'], slow_period)

    # Detect crossover: fast crosses above slow
    crossover = (fast_ema > slow_ema) & (fast_ema.shift(1) <= slow_ema.shift(1))

    # Apply volume filter if enabled
    if volume_filter and 'Volume' in df.columns:
        avg_volume = df['Volume'].rolling(20).mean()
        volume_check = df['Volume'] > avg_volume
        crossover = crossover & volume_check

    return crossover


def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        df: DataFrame with price data
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)

    Returns:
        tuple: (MACD line, Signal line, Histogram)
    """
    fast_ema = calculate_ema(df['Close'], fast)
    slow_ema = calculate_ema(df['Close'], slow)

    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def macd_cross(df: pd.DataFrame, fast=12, slow=26, signal=9, histogram_confirm=True) -> pd.Series:
    """
    Detect MACD Cross with Histogram Confirmation.

    Returns boolean Series: True when MACD crosses above signal line.

    Rules:
    - MACD line crosses above signal line
    - Optional histogram confirmation: histogram must be positive and increasing
    - Uses shift(1) to avoid look-ahead bias
    """
    macd_line, signal_line, histogram = calculate_macd(df, fast, slow, signal)

    # Detect crossover: MACD crosses above signal
    crossover = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))

    # Apply histogram confirmation if enabled
    if histogram_confirm:
        # Histogram positive and increasing
        hist_positive = histogram > 0
        hist_increasing = histogram > histogram.shift(1)
        crossover = crossover & hist_positive & hist_increasing

    return crossover
