# backtester.py
"""
Vectorized backtester with no look-ahead bias.

All signals use prior-day data only.
Entry/exit on close prices.
"""
import pandas as pd
import numpy as np


def vectorized_backtest(df: pd.DataFrame, signal: pd.Series, initial_cash=100_000):
    """
    Vectorized backtest engine.

    Args:
        df: DataFrame with OHLCV data
        signal: Boolean Series aligned with df.index (True = buy signal)
        initial_cash: Starting portfolio value

    Returns:
        dict with:
            - equity: Series of portfolio value over time
            - total_return: Final return percentage
            - cagr: Compound Annual Growth Rate
            - sharpe: Sharpe ratio (annualized)
            - max_dd: Maximum drawdown
            - win_rate: Percentage of winning trades
            - num_trades: Total number of trades
            - signal_dates: List of signal dates
    """
    # Align signal with df index
    sig = signal.reindex(df.index).fillna(False).astype(bool)

    # Calculate daily returns
    returns = df['Close'].pct_change().fillna(0)

    # Strategy returns: enter on close, exit next close
    # shift(1) ensures we use prior signals (no look-ahead)
    strategy_returns = returns.shift(-1) * sig.shift(1)
    strategy_returns = strategy_returns.fillna(0)

    # Build equity curve
    equity = (1 + strategy_returns).cumprod() * initial_cash
    equity.iloc[0] = initial_cash

    # Calculate metrics
    total_return = equity.iloc[-1] / initial_cash - 1

    # CAGR: annualized return
    years = len(equity) / 252  # 252 trading days per year
    cagr = (equity.iloc[-1] / initial_cash) ** (1 / years) - 1 if years > 0 else 0

    # Sharpe ratio: risk-adjusted return (annualized)
    mean_return = strategy_returns.mean()
    std_return = strategy_returns.std()
    sharpe = np.sqrt(252) * mean_return / std_return if std_return > 0 else np.nan

    # Maximum drawdown
    running_max = equity.cummax()
    drawdown = (equity / running_max - 1)
    max_dd = drawdown.min()

    # Win rate
    winning_trades = strategy_returns > 0
    win_rate = winning_trades.sum() / sig.sum() if sig.sum() > 0 else 0

    # Number of trades
    num_trades = sig.sum()

    # Signal dates
    signal_dates = df.index[sig].tolist()

    return {
        'equity': equity,
        'total_return': total_return,
        'cagr': cagr,
        'sharpe': sharpe,
        'max_dd': max_dd,
        'win_rate': win_rate,
        'num_trades': num_trades,
        'signal_dates': signal_dates
    }
