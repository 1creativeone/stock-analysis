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
