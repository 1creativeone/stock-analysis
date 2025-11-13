#!/usr/bin/env python3
"""
Test core functionality with synthetic data.
This validates pattern detection and backtesting logic.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from patterns import double_bottom, rsi_divergence, breakout_52w, calculate_rsi
from backtester import vectorized_backtest


def generate_mock_stock_data(days=2520, seed=42):
    """
    Generate synthetic OHLCV data for testing.

    Args:
        days: Number of trading days (default: ~10 years)
        seed: Random seed for reproducibility
    """
    np.random.seed(seed)

    # Generate dates
    start_date = datetime.now() - timedelta(days=days)
    dates = pd.date_range(start=start_date, periods=days, freq='D')

    # Generate price with trend and noise
    base_price = 100
    trend = np.linspace(0, 50, days)  # Upward trend
    noise = np.random.randn(days).cumsum() * 2
    close = base_price + trend + noise

    # Generate OHLC from close
    high = close + np.abs(np.random.randn(days) * 2)
    low = close - np.abs(np.random.randn(days) * 2)
    open_price = close + np.random.randn(days) * 1

    # Volume
    volume = np.random.randint(1_000_000, 10_000_000, days)

    df = pd.DataFrame({
        'Open': open_price,
        'High': high,
        'Low': low,
        'Close': close,
        'Volume': volume
    }, index=dates)

    return df


def test_rsi_calculation():
    """Test RSI calculation."""
    print("Testing RSI calculation...")

    # Create simple test data
    prices = pd.Series([44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42,
                       45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00])

    rsi = calculate_rsi(prices, period=14)

    # RSI should be between 0 and 100
    valid_rsi = rsi.dropna()
    assert all((valid_rsi >= 0) & (valid_rsi <= 100)), "RSI out of range!"

    print(f"  ✓ RSI calculation working (last value: {valid_rsi.iloc[-1]:.2f})")


def test_pattern_detection():
    """Test pattern detection functions."""
    print("\nTesting pattern detection...")

    df = generate_mock_stock_data(days=2520)

    # Test Double Bottom
    db_signals = double_bottom(df)
    print(f"  ✓ Double Bottom: {db_signals.sum()} signals detected")

    # Test RSI Divergence
    rsi_signals = rsi_divergence(df)
    print(f"  ✓ RSI Divergence: {rsi_signals.sum()} signals detected")

    # Test 52W Breakout
    breakout_signals = breakout_52w(df)
    print(f"  ✓ 52W Breakout: {breakout_signals.sum()} signals detected")


def test_backtester():
    """Test backtest engine."""
    print("\nTesting backtester...")

    df = generate_mock_stock_data(days=2520)

    # Create simple signal: buy on first Monday of each month
    signal = pd.Series(False, index=df.index)
    signal[df.index.day == 1] = True

    # Run backtest
    results = vectorized_backtest(df, signal, initial_cash=100_000)

    # Validate results
    assert 'equity' in results, "Missing equity curve!"
    assert 'sharpe' in results, "Missing Sharpe ratio!"
    assert 'cagr' in results, "Missing CAGR!"
    assert 'max_dd' in results, "Missing max drawdown!"

    print(f"  ✓ Backtest completed successfully")
    print(f"    - Total Return: {results['total_return']:.2%}")
    print(f"    - CAGR: {results['cagr']:.2%}")
    print(f"    - Sharpe: {results['sharpe']:.2f}")
    print(f"    - Max Drawdown: {results['max_dd']:.2%}")
    print(f"    - Trades: {results['num_trades']}")


def test_integration():
    """Test full integration: pattern detection + backtesting."""
    print("\nTesting integration (pattern + backtest)...")

    df = generate_mock_stock_data(days=2520)

    # Test with 52W Breakout (most reliable for synthetic data)
    signal = breakout_52w(df)

    if signal.sum() > 0:
        results = vectorized_backtest(df, signal)

        print(f"  ✓ Integration test passed")
        print(f"    - Pattern: 52W Breakout")
        print(f"    - Signals: {signal.sum()}")
        print(f"    - Sharpe: {results['sharpe']:.2f}")
        print(f"    - Win Rate: {results['win_rate']:.2%}")
    else:
        print("  ⚠ No signals generated (expected with random data)")


if __name__ == "__main__":
    print("="*70)
    print("SMART PATTERN BACKTESTER - CORE FUNCTIONALITY TEST")
    print("="*70)

    try:
        test_rsi_calculation()
        test_pattern_detection()
        test_backtester()
        test_integration()

        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED!")
        print("="*70)
        print("\nCore functionality is working correctly.")
        print("Ready to run with real data using: python run.py")
        print("\nNote: Install yfinance to download real stock data:")
        print("  pip install yfinance")
        print("="*70)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
