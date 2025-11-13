# config.py
"""
Configuration file for Smart Pattern Backtester.

All user-configurable parameters in one place.
"""

# ==================== DATA SETTINGS ====================
DATA_CONFIG = {
    # Data source
    'period': '10y',  # yfinance period: 1y, 5y, 10y, max
    'interval': '1d',  # yfinance interval: 1d, 1wk, 1mo

    # Caching
    'cache_dir': 'data',
    'use_cache': True,  # Use cached data if available
    'cache_expiry_days': 7,  # Re-download if older than N days
}

# ==================== PATTERN SETTINGS ====================
PATTERN_CONFIG = {
    # Double Bottom
    'double_bottom': {
        'enabled': True,
        'window': 20,  # Look for patterns within N bars
        'tolerance': 0.03,  # Troughs within ±3% price
    },

    # RSI Divergence
    'rsi_divergence': {
        'enabled': True,
        'rsi_period': 14,  # RSI calculation period
        'lookback': 30,  # Bars to look back for divergence
    },

    # 52-Week Breakout
    'breakout_52w': {
        'enabled': True,
        'period': 252,  # Trading days in a year
    }
}

# ==================== BACKTEST SETTINGS ====================
BACKTEST_CONFIG = {
    'initial_cash': 100_000,  # Starting portfolio value
    'position_size': 1.0,  # Fraction of portfolio per trade (1.0 = all-in)
    'commission': 0.0,  # Commission per trade (0.001 = 0.1%)
    'slippage': 0.0,  # Slippage per trade (0.001 = 0.1%)
}

# ==================== SCANNER SETTINGS ====================
SCANNER_CONFIG = {
    # Which tickers to scan
    'ticker_source': 'sp500',  # 'sp500', 'custom', 'file'
    'custom_tickers': ['AAPL', 'MSFT', 'GOOGL'],  # Used if ticker_source='custom'
    'ticker_file': 'tickers.txt',  # Used if ticker_source='file'

    # Filtering
    'min_data_points': 500,  # Minimum bars required
    'min_trades': 3,  # Minimum trades to include signal
    'min_sharpe': None,  # Minimum Sharpe (None = no filter)

    # Output
    'top_n': 5,  # Number of top signals to return
    'save_all_signals': True,  # Save all signals to CSV
    'generate_plots': True,  # Generate equity curve plots
}

# ==================== RISK METRICS ====================
RISK_CONFIG = {
    'risk_free_rate': 0.0,  # Annual risk-free rate for Sharpe calculation
    'trading_days_per_year': 252,
}

# ==================== OUTPUT SETTINGS ====================
OUTPUT_CONFIG = {
    'results_dir': 'results',
    'top_signals_file': 'top_5.csv',
    'all_signals_file': 'all_signals_{timestamp}.csv',
    'equity_plot_file': 'top_equity.png',

    # Plot settings
    'plot_dpi': 300,
    'plot_style': 'seaborn-v0_8-darkgrid',  # matplotlib style
}

# ==================== DASHBOARD SETTINGS ====================
DASHBOARD_CONFIG = {
    'page_title': 'Smart Pattern Backtester',
    'page_icon': '📈',
    'layout': 'wide',

    # Features
    'enable_lead_capture': True,
    'enable_scanner_button': True,
    'enable_trade_details': True,

    # Display
    'default_dark_mode': True,
    'cache_ttl': 300,  # Seconds to cache data
}

# ==================== EMAIL SETTINGS ====================
EMAIL_CONFIG = {
    'enabled': False,  # Enable email alerts
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'alerts@example.com',
    'sender_password': '',  # Use environment variable in production
    'recipient_email': 'you@example.com',

    # Email content
    'subject_template': 'Top 5 Signals - {date}',
    'send_on_scan': True,  # Send email after each scan
}

# ==================== ADVANCED SETTINGS ====================
ADVANCED_CONFIG = {
    # Optimization
    'multiprocessing': False,  # Use multiprocessing (experimental)
    'max_workers': 4,  # Number of parallel workers

    # Debugging
    'verbose': True,  # Print debug information
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR

    # Experimental
    'enable_ml_classifier': False,  # Future: ML pattern classifier
}


# ==================== HELPER FUNCTIONS ====================

def get_pattern_config(pattern_name):
    """Get config for a specific pattern."""
    pattern_map = {
        'Double Bottom': 'double_bottom',
        'RSI Divergence': 'rsi_divergence',
        '52W Breakout': 'breakout_52w'
    }
    key = pattern_map.get(pattern_name)
    return PATTERN_CONFIG.get(key, {})


def is_pattern_enabled(pattern_name):
    """Check if a pattern is enabled."""
    config = get_pattern_config(pattern_name)
    return config.get('enabled', True)


def get_enabled_patterns():
    """Get list of enabled pattern names."""
    patterns = []
    if PATTERN_CONFIG['double_bottom']['enabled']:
        patterns.append('Double Bottom')
    if PATTERN_CONFIG['rsi_divergence']['enabled']:
        patterns.append('RSI Divergence')
    if PATTERN_CONFIG['breakout_52w']['enabled']:
        patterns.append('52W Breakout')
    return patterns


# ==================== VALIDATION ====================

def validate_config():
    """Validate configuration settings."""
    errors = []

    # Validate backtest settings
    if BACKTEST_CONFIG['initial_cash'] <= 0:
        errors.append("initial_cash must be positive")

    if not (0 < BACKTEST_CONFIG['position_size'] <= 1):
        errors.append("position_size must be between 0 and 1")

    # Validate scanner settings
    if SCANNER_CONFIG['top_n'] <= 0:
        errors.append("top_n must be positive")

    if SCANNER_CONFIG['min_trades'] < 0:
        errors.append("min_trades must be non-negative")

    # Validate pattern settings
    for pattern, config in PATTERN_CONFIG.items():
        if not isinstance(config.get('enabled', True), bool):
            errors.append(f"{pattern}.enabled must be boolean")

    return errors


if __name__ == "__main__":
    """Print current configuration."""
    print("=" * 80)
    print("SMART PATTERN BACKTESTER - CONFIGURATION")
    print("=" * 80)

    print("\n📊 DATA SETTINGS:")
    for key, value in DATA_CONFIG.items():
        print(f"  {key}: {value}")

    print("\n🎯 PATTERN SETTINGS:")
    for pattern, config in PATTERN_CONFIG.items():
        print(f"  {pattern}:")
        for key, value in config.items():
            print(f"    {key}: {value}")

    print("\n💰 BACKTEST SETTINGS:")
    for key, value in BACKTEST_CONFIG.items():
        print(f"  {key}: {value}")

    print("\n🔍 SCANNER SETTINGS:")
    for key, value in SCANNER_CONFIG.items():
        print(f"  {key}: {value}")

    print("\n✅ ENABLED PATTERNS:")
    for pattern in get_enabled_patterns():
        print(f"  - {pattern}")

    # Validate
    errors = validate_config()
    if errors:
        print("\n❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configuration valid!")

    print("=" * 80)
