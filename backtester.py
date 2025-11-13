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

    # Sortino Ratio: like Sharpe but only penalizes downside volatility
    downside_returns = strategy_returns[strategy_returns < 0]
    downside_std = downside_returns.std()
    sortino = np.sqrt(252) * mean_return / downside_std if downside_std > 0 else np.nan

    # Calmar Ratio: CAGR / Max Drawdown
    calmar = abs(cagr / max_dd) if max_dd != 0 else np.nan

    # Profit Factor: Gross Profits / Gross Losses
    gross_profits = strategy_returns[strategy_returns > 0].sum()
    gross_losses = abs(strategy_returns[strategy_returns < 0].sum())
    profit_factor = gross_profits / gross_losses if gross_losses != 0 else np.nan

    # Max consecutive wins/losses
    trade_results = strategy_returns[sig.shift(1).fillna(False)]
    wins = (trade_results > 0).astype(int)
    losses = (trade_results < 0).astype(int)

    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_wins = 0
    current_losses = 0

    for result in trade_results:
        if result > 0:
            current_wins += 1
            current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
        elif result < 0:
            current_losses += 1
            current_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, current_losses)
        else:
            current_wins = 0
            current_losses = 0

    return {
        'equity': equity,
        'total_return': total_return,
        'cagr': cagr,
        'sharpe': sharpe,
        'sortino': sortino,
        'calmar': calmar,
        'profit_factor': profit_factor,
        'max_dd': max_dd,
        'win_rate': win_rate,
        'num_trades': num_trades,
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        'signal_dates': signal_dates
    }
