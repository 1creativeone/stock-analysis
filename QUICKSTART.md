# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/yourname/stock-analysis.git
cd stock-analysis

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Run Tests (No Real Data Needed)

```bash
# Test core functionality
python test_core.py

# Run transparency audit
python audit.py

# Test configuration
python config.py

# Test export functionality
python export.py
```

### 2. Run Scanner (Requires Real Data)

```bash
# Install yfinance for real stock data
pip install yfinance

# Run full S&P 500 scan (takes 3-5 minutes)
python run.py
```

**Output:**
- `results/top_5.csv` - Top 5 signals ranked by Sharpe
- `results/all_signals_*.csv` - All detected signals
- `results/top_equity.png` - Equity curve visualization
- `data/*.csv` - Cached stock data (for faster subsequent runs)

### 3. Launch Dashboard

```bash
# Start Streamlit dashboard
streamlit run dashboard.py
```

Opens at: http://localhost:8501

**Features:**
- 📊 Interactive equity curves
- 🔍 Signal deep dive with candlestick charts
- 📈 Pattern performance comparison
- 📋 Trade-level drill-down
- 💌 Email lead capture
- 🔄 One-click scanner refresh

### 4. Generate Sample Data (For Testing)

```bash
# Create sample results without running full scan
python generate_sample_data.py

# Then launch dashboard
streamlit run dashboard.py
```

## Configuration

Edit `config.py` to customize:

```python
# Pattern settings
PATTERN_CONFIG = {
    'double_bottom': {
        'enabled': True,
        'window': 20,
        'tolerance': 0.03,
    },
    # ... more settings
}

# Scanner settings
SCANNER_CONFIG = {
    'top_n': 5,
    'min_trades': 3,
    # ... more settings
}
```

## Export Results

```python
from export import export_results
import pandas as pd

# Load results
df = pd.read_csv('results/top_5.csv')

# Export to all formats
export_results(df, format='all')
```

**Output:**
- `exports/results_*.csv` - CSV format
- `exports/report_*.md` - Markdown report
- `exports/report_*.txt` - Text report

## Transparency Audit

```bash
# Run full audit
python audit.py
```

**Checks:**
- ✅ Data integrity
- ✅ RSI calculation accuracy
- ✅ Pattern detection validity
- ✅ Backtest engine (no look-ahead bias)
- ✅ Results reproducibility
- ✅ No overfitting

## Project Structure

```
stock-analysis/
├── patterns.py              # Pattern detectors
├── backtester.py           # Backtest engine
├── screener.py             # S&P 500 scanner
├── dashboard.py            # Streamlit UI
├── config.py               # Configuration
├── export.py               # Export utilities
├── audit.py                # Transparency audit
├── run.py                  # Entry point
├── test_core.py            # Test suite
├── generate_sample_data.py # Sample data generator
├── requirements.txt        # Dependencies
├── data/                   # Stock data cache
├── results/                # Scan results
└── exports/                # Exported reports
```

## Common Workflows

### Daily Workflow
1. `python run.py` - Run morning scan
2. `streamlit run dashboard.py` - View results
3. Review top 5 signals
4. Check trade details

### Development Workflow
1. `python test_core.py` - Test changes
2. `python audit.py` - Verify transparency
3. `python run.py` - Test with real data
4. `streamlit run dashboard.py` - Test UI

### Analysis Workflow
1. Run scanner
2. Export results: `python export.py`
3. Review markdown report
4. Compare patterns in dashboard

## Tips

**Speed up scans:**
- Data is cached in `data/` directory
- Subsequent scans are much faster
- Delete `data/` to force refresh

**Customize patterns:**
- Edit thresholds in `config.py`
- Modify detection logic in `patterns.py`
- Run `python test_core.py` to verify

**Deploy dashboard:**
- Streamlit Cloud (free): https://streamlit.io/cloud
- Railway: https://railway.app
- Render: https://render.com

## Troubleshooting

**No signals found:**
- Reduce `min_trades` in `config.py`
- Check pattern thresholds
- Verify data quality

**Dashboard won't start:**
- Install streamlit: `pip install streamlit`
- Check port 8501 is available
- Run with: `streamlit run dashboard.py --server.port 8502`

**Slow scans:**
- First run downloads 10 years of data
- Use smaller ticker list for testing
- Enable caching in `config.py`

## Next Steps

- [ ] Run full S&P 500 scan
- [ ] Deploy dashboard to Streamlit Cloud
- [ ] Set up email alerts
- [ ] Schedule daily scans with cron
- [ ] Customize patterns for your strategy

## Support

- Documentation: See `IMPLEMENTATION_STATUS.md`
- Transparency: See `audit.py`
- Configuration: See `config.py`
- Issues: [GitHub Issues](#)
