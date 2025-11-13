#!/usr/bin/env python3
"""
Generate sample data for testing the dashboard without running full scanner.
"""
import pandas as pd
import os

# Create results directory
os.makedirs('results', exist_ok=True)

# Sample top 5 results
sample_data = pd.DataFrame({
    'ticker': ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL'],
    'pattern': ['52W Breakout', 'Double Bottom', 'RSI Divergence', '52W Breakout', 'Double Bottom'],
    'sharpe': [2.15, 1.92, 1.78, 1.65, 1.53],
    'cagr': [0.48, 0.41, 0.35, 0.31, 0.28],
    'max_dd': [-0.31, -0.38, -0.29, -0.25, -0.33],
    'win_rate': [0.68, 0.65, 0.62, 0.64, 0.60],
    'num_trades': [12, 8, 15, 10, 14],
    'latest_signal': pd.to_datetime([
        '2024-11-10',
        '2024-11-08',
        '2024-11-05',
        '2024-11-03',
        '2024-10-28'
    ])
})

# Save to CSV
output_path = 'results/top_5.csv'
sample_data.to_csv(output_path, index=False)
print(f"✅ Created sample data: {output_path}")
print(f"\nSample data preview:")
print(sample_data)
