#!/usr/bin/env python3
# run.py
"""
Smart Pattern Backtester - Entry Point

One-click scanner that finds the best technical patterns
backed by 10 years of historical data.

Usage:
    python run.py
"""
from screener import run_full_scan


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        SMART PATTERN BACKTESTER                               ║
║        Find patterns that work — with proof.                  ║
║                                                               ║
║        • Scans S&P 500 stocks                                 ║
║        • Detects 3 proven patterns                            ║
║        • 10-year vectorized backtest                          ║
║        • Ranks by Sharpe ratio                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # Run the scanner
    # Adjust top_n to get more/fewer results
    run_full_scan(top_n=5)

    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  ✓ Scan Complete!                                             ║
║                                                               ║
║  Next Steps:                                                  ║
║  • View results in results/top_5.csv                          ║
║  • Check equity curves in results/top_equity.png              ║
║  • Run: streamlit run dashboard.py (coming in Phase 2)        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
