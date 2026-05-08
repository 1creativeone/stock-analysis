#!/usr/bin/env python3
# dashboard.py
"""
Pattern Backtester — Do Not Copy Trade
Rule-based technical pattern analysis backed by historical data.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from PIL import Image
import os
import sys
from datetime import datetime
import subprocess

# Import local modules
from patterns import double_bottom, rsi_divergence, breakout_52w, ema_crossover, macd_cross, cup_and_handle, bollinger_reversion
from backtester import vectorized_backtest

# ==================== CONFIG ====================
_favicon = Image.open("favicon.png") if os.path.exists("favicon.png") else "📊"

st.set_page_config(
    page_title="Pattern Backtester — Do Not Copy Trade",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

RESULT_DIR = "results"
DATA_DIR = "data"
TOP_CSV = f"{RESULT_DIR}/top_5.csv"

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
    }
    .big-metric {
        font-size: 24px;
        font-weight: 700;
        color: #4fc7bb;
    }
    .stMetric {
        background-color: #eeede8;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #d9d6cf;
    }
    .stMetric label {
        color: #6b6356 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #28251d !important;
        font-weight: 700;
    }
    .success-box {
        padding: 10px;
        background-color: #e6faf8;
        border-left: 4px solid #4fc7bb;
        border-radius: 4px;
        margin: 10px 0;
    }
    .info-box {
        padding: 10px;
        background-color: #f0faf9;
        border-left: 4px solid #4fc7bb;
        border-radius: 4px;
        margin: 10px 0;
    }
    [data-testid="stSidebar"] {
        background-color: #efede9 !important;
        border-right: 1px solid #d9d6cf;
    }
    .dataframe thead th {
        background-color: #eeede8 !important;
        color: #28251d !important;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_results():
    """Load top results CSV."""
    if not os.path.exists(TOP_CSV):
        return None
    df = pd.read_csv(TOP_CSV)
    if 'latest_signal' in df.columns:
        df['latest_signal'] = pd.to_datetime(df['latest_signal'], format='mixed', utc=True).dt.tz_localize(None)
    return df


def load_stock_data(ticker):
    """Load cached stock data for a ticker."""
    path = f"{DATA_DIR}/{ticker}.csv"
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df


def get_pattern_signal(df, pattern_name):
    """Generate signal for a specific pattern."""
    if pattern_name == 'Double Bottom':
        return double_bottom(df)
    elif pattern_name == 'RSI Divergence':
        return rsi_divergence(df)
    elif pattern_name == '52W Breakout':
        return breakout_52w(df)
    elif pattern_name == 'EMA Crossover':
        return ema_crossover(df)
    elif pattern_name == 'MACD Cross':
        return macd_cross(df)
    elif pattern_name == 'Cup & Handle':
        return cup_and_handle(df)
    elif pattern_name == 'Bollinger Reversion':
        return bollinger_reversion(df)
    return None


def run_scanner():
    """Run the backtester scanner."""
    try:
        result = subprocess.run(
            [sys.executable, "run.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### Do Not Copy Trade")
    st.caption("Pattern Backtester — rule-based, no black boxes.")

    st.markdown("---")

    # Scanner control
    st.subheader("Scanner")

    if st.button("Run Full Scan", type="primary", use_container_width=True):
        with st.spinner("Running scanner... This may take 3-5 minutes."):
            success, stdout, stderr = run_scanner()
            if success:
                st.success("✅ Scan complete!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Scan failed")
                with st.expander("Error Details"):
                    st.code(stderr)

    # Last updated
    if os.path.exists(TOP_CSV):
        mod_time = datetime.fromtimestamp(os.path.getmtime(TOP_CSV))
        st.info(f"📅 Last scan: {mod_time.strftime('%b %d, %Y %I:%M %p')}")

    st.markdown("---")

    # Settings
    st.subheader("Settings")
    show_trades = st.checkbox("Show Trade Details", value=True)

    st.markdown("---")

    # Stats
    st.subheader("Stats")
    if os.path.exists(DATA_DIR):
        cached_tickers = len([f for f in os.listdir(DATA_DIR) if f.endswith('.csv')])
        st.metric("Cached Tickers", cached_tickers)

    st.markdown("---")
    st.caption("Educational only. Not financial advice.")
    st.caption("donotcopytrade.com")


# ==================== MAIN CONTENT ====================

# Header
st.markdown("## Pattern Backtester")
st.markdown("Rule-based technical patterns backed by 10 years of historical data. No AI, no black boxes. Educational only — not financial advice.")

# Load results
results_df = load_results()

if results_df is None or results_df.empty:
    st.warning("⚠️ No results yet. Click **Run Full Scan** in the sidebar to start.")
    st.info("""
    **What happens during a scan:**
    1. Fetches 10 years of daily stock data for S&P 500 companies
    2. Detects 3 proven technical patterns
    3. Backtests each pattern with no look-ahead bias
    4. Ranks by Sharpe ratio (risk-adjusted returns)
    5. Saves top 5 signals

    **First run typically takes 3-5 minutes. Subsequent runs are faster with cached data.**
    """)
    st.stop()

# ==================== KPI CARDS ====================
st.markdown("### Performance Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    avg_sharpe = results_df['sharpe'].mean()
    st.metric("Avg Sharpe", f"{avg_sharpe:.2f}",
              delta="Higher is better" if avg_sharpe > 1.0 else None)

with col2:
    avg_cagr = results_df['cagr'].mean()
    st.metric("Avg CAGR", f"{avg_cagr:.1%}")

with col3:
    best_sharpe = results_df['sharpe'].max()
    st.metric("Best Sharpe", f"{best_sharpe:.2f}")

with col4:
    total_signals = len(results_df)
    st.metric("Total Signals", total_signals)

with col5:
    avg_trades = results_df['num_trades'].mean()
    st.metric("Avg Trades", f"{avg_trades:.0f}")

st.markdown("---")

# ==================== FILTERS ====================
st.markdown("### Filter Results")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Pattern filter
    all_patterns = ['All'] + sorted(results_df['pattern'].unique().tolist())
    pattern_filter = st.selectbox("Pattern", all_patterns)

with col2:
    # Sharpe filter
    min_sharpe = st.number_input("Min Sharpe", value=0.0, step=0.1, format="%.1f")

with col3:
    # CAGR filter
    min_cagr = st.number_input("Min CAGR (%)", value=0.0, step=5.0, format="%.1f")

with col4:
    # Min trades filter
    min_trades_filter = st.number_input("Min Trades", value=1, step=1, min_value=1)

# Apply filters
filtered_df = results_df.copy()

if pattern_filter != 'All':
    filtered_df = filtered_df[filtered_df['pattern'] == pattern_filter]

filtered_df = filtered_df[filtered_df['sharpe'] >= min_sharpe]
filtered_df = filtered_df[filtered_df['cagr'] >= (min_cagr / 100)]
filtered_df = filtered_df[filtered_df['num_trades'] >= min_trades_filter]

st.caption(f"Showing {len(filtered_df)} of {len(results_df)} signals")

st.markdown("---")

# ==================== TOP SIGNALS TABLE ====================
st.markdown("### Top Signals (Ranked by Sharpe)")

# Format the display
display_df = filtered_df.copy()
display_df['sharpe'] = display_df['sharpe'].apply(lambda x: f"{x:.2f}")
display_df['cagr'] = display_df['cagr'].apply(lambda x: f"{x:.1%}")
display_df['max_dd'] = display_df['max_dd'].apply(lambda x: f"{x:.1%}")
display_df['win_rate'] = display_df['win_rate'].apply(lambda x: f"{x:.1%}")

display_cols = ['ticker', 'pattern', 'sharpe', 'cagr', 'max_dd', 'win_rate', 'num_trades', 'latest_signal']
st.dataframe(
    display_df[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "ticker": "Ticker",
        "pattern": "Pattern",
        "sharpe": "Sharpe",
        "cagr": "CAGR",
        "max_dd": "Max DD",
        "win_rate": "Win Rate",
        "num_trades": "Trades",
        "latest_signal": "Latest Signal"
    }
)

st.markdown("---")

# ==================== EQUITY CURVES ====================
st.markdown("### Equity Curves (Normalized to $100K)")

fig = go.Figure()

colors = ["#4fc7bb", "#c2896e", "#7bbfa8", "#8ab4e8", "#d9a44a"]

for idx, (_, row) in enumerate(results_df.head(5).iterrows()):
    ticker = row['ticker']
    pattern = row['pattern']

    # Load data
    df = load_stock_data(ticker)
    if df is None:
        continue

    # Get signal
    signal = get_pattern_signal(df, pattern)
    if signal is None:
        continue

    # Run backtest
    bt = vectorized_backtest(df, signal)

    # Plot
    fig.add_trace(go.Scatter(
        x=bt['equity'].index,
        y=bt['equity'],
        name=f"{ticker} — {pattern} (Sharpe: {row['sharpe']:.2f})",
        line=dict(color=colors[idx % len(colors)], width=2),
        hovertemplate='%{x|%Y-%m-%d}<br>$%{y:,.0f}<extra></extra>'
    ))

fig.update_layout(
    height=500,
    xaxis_title="Date",
    yaxis_title="Portfolio Value ($)",
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255,255,255,0.8)"
    ),
    template="plotly_white",
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==================== PATTERN COMPARISON ====================
st.markdown("### Pattern Performance Comparison")

col1, col2 = st.columns(2)

with col1:
    # Sharpe by Pattern
    pattern_sharpe = results_df.groupby('pattern')['sharpe'].mean().sort_values(ascending=False)

    fig_sharpe = go.Figure(data=[
        go.Bar(
            x=pattern_sharpe.index,
            y=pattern_sharpe.values,
            marker_color=['#4fc7bb', '#c2896e', '#7bbfa8'],
            text=pattern_sharpe.values.round(2),
            textposition='auto',
        )
    ])
    fig_sharpe.update_layout(
        title="Average Sharpe by Pattern",
        xaxis_title="Pattern",
        yaxis_title="Sharpe Ratio",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_sharpe, use_container_width=True)

with col2:
    # Win Rate by Pattern
    pattern_winrate = results_df.groupby('pattern')['win_rate'].mean().sort_values(ascending=False)

    fig_wr = go.Figure(data=[
        go.Bar(
            x=pattern_winrate.index,
            y=pattern_winrate.values * 100,
            marker_color=['#7bbfa8', '#4fc7bb', '#d9a44a'],
            text=[f"{x:.1f}%" for x in pattern_winrate.values * 100],
            textposition='auto',
        )
    ])
    fig_wr.update_layout(
        title="Average Win Rate by Pattern",
        xaxis_title="Pattern",
        yaxis_title="Win Rate (%)",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_wr, use_container_width=True)

st.markdown("---")

# ==================== SIGNAL DEEP DIVE ====================
st.markdown("### Deep Dive: Explore Any Signal")

selected_idx = st.selectbox(
    "Select a signal to analyze",
    range(len(results_df)),
    format_func=lambda i: f"{results_df.iloc[i]['ticker']} — {results_df.iloc[i]['pattern']} (Sharpe: {results_df.iloc[i]['sharpe']:.2f})"
)

row = results_df.iloc[selected_idx]

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("#### Signal Details")
    st.markdown(f"""
    - **Ticker:** `{row['ticker']}`
    - **Pattern:** {row['pattern']}
    - **Sharpe Ratio:** {row['sharpe']:.2f}
    - **CAGR:** {row['cagr']:.2%}
    - **Max Drawdown:** {row['max_dd']:.2%}
    - **Win Rate:** {row['win_rate']:.2%}
    - **Trades:** {int(row['num_trades'])}
    - **Latest Signal:** {row['latest_signal'].strftime('%Y-%m-%d') if pd.notna(row['latest_signal']) else 'N/A'}
    """)

with col2:
    # Load ticker data
    ticker_df = load_stock_data(row['ticker'])

    if ticker_df is not None:
        # Show recent price action
        recent = ticker_df[-252:]  # Last year

        fig_detail = go.Figure()

        # Candlestick
        fig_detail.add_trace(go.Candlestick(
            x=recent.index,
            open=recent['Open'],
            high=recent['High'],
            low=recent['Low'],
            close=recent['Close'],
            name="Price"
        ))

        # Add signal marker if recent
        if pd.notna(row['latest_signal']) and row['latest_signal'] in recent.index:
            signal_date = row['latest_signal']
            signal_price = recent.loc[signal_date, 'Close']

            fig_detail.add_trace(go.Scatter(
                x=[signal_date],
                y=[signal_price],
                mode='markers',
                marker=dict(size=15, color='gold', symbol='star', line=dict(color='black', width=2)),
                name='Signal',
                hovertemplate=f'Signal: {signal_date.strftime("%Y-%m-%d")}<br>Price: ${signal_price:.2f}<extra></extra>'
            ))

        fig_detail.update_layout(
            title=f"{row['ticker']} — Last 12 Months",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            template="plotly_white",
            height=400,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig_detail, use_container_width=True)

# Show trade details if enabled
if show_trades and ticker_df is not None:
    st.markdown("#### Trade History")

    # Get signal
    signal = get_pattern_signal(ticker_df, row['pattern'])

    if signal is not None and signal.sum() > 0:
        # Get signal dates
        signal_dates = ticker_df.index[signal]

        # Build trade table
        trades = []
        for date in signal_dates:
            if date in ticker_df.index:
                entry_price = ticker_df.loc[date, 'Close']

                # Find exit (next day)
                try:
                    exit_idx = ticker_df.index.get_loc(date) + 1
                    if exit_idx < len(ticker_df):
                        exit_date = ticker_df.index[exit_idx]
                        exit_price = ticker_df.loc[exit_date, 'Close']
                        pnl = (exit_price - entry_price) / entry_price

                        trades.append({
                            'Entry Date': date.strftime('%Y-%m-%d'),
                            'Entry Price': f"${entry_price:.2f}",
                            'Exit Date': exit_date.strftime('%Y-%m-%d'),
                            'Exit Price': f"${exit_price:.2f}",
                            'P&L': f"{pnl:.2%}",
                            'Result': '✅ Win' if pnl > 0 else '❌ Loss'
                        })
                except:
                    pass

        if trades:
            trades_df = pd.DataFrame(trades)
            st.dataframe(trades_df, use_container_width=True, hide_index=True)
        else:
            st.info("No complete trades to display")

st.markdown("---")

# ==================== FOOTER ====================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**No AI. No ML. Just Logic.**")
    st.caption("100% rule-based, transparent, and auditable")

with col2:
    st.markdown("**Open Source**")
    st.caption("All pattern logic is fully auditable")

with col3:
    st.markdown("**Educational Only**")
    st.caption("Not financial advice. See the [disclaimer](https://donotcopytrade.com/disclaimer).")

st.markdown("---")
st.caption(f"© {datetime.now().year} Do Not Copy Trade | Pattern Backtester | Educational only — not financial advice")
