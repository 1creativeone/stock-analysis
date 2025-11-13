# stock-analysis

---

## `README.md` – GitHub Ready

```md
# Smart Pattern Backtester

**Find patterns that work — with proof.**

A **rules-based stock screener** that scans the S&P 500 nightly, detects 3 high-conviction technical patterns, backtests them over **10 years**, and surfaces the **top 5 signals** by **Sharpe ratio**.

**No AI. No machine learning. Just logic, history, and performance.**

[![No AI](https://img.shields.io/badge/AI-None-brightgreen)](https://img.shields.io)
[![Backtested](https://img.shields.io/badge/Backtested-10%20Years-blue)](https://img.shields.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Live Demo: [https://your-app.streamlit.app](https://your-app.streamlit.app) *(deploy in 2 mins)*

---

## Why This Exists

> Most screeners show **patterns**.  
> **We show which ones made money.**

Every signal includes:
- Clear entry/exit rules
- 10-year equity curve
- Sharpe ratio, CAGR, max drawdown
- Number of trades
- Full code to verify

**If it doesn’t make money in backtest — it doesn’t make the list.**

---

## Features

| Feature | Status |
|-------|--------|
| Scans 500+ S&P 500 stocks | Done |
| Detects Double Bottom, RSI Divergence, 52W Breakout | Done |
| 10-year vectorized backtest (no look-ahead) | Done |
| Ranks by Sharpe ratio | Done |
| Interactive Streamlit dashboard | Done |
| One-click refresh | Done |
| CSV + equity curve export | Done |
| Lead capture form | Done |

---

## Live Dashboard

![Top Equity Curves](results/top_equity.png)

---

## Quick Start

```bash
git clone https://github.com/yourname/smart-pattern-backtester.git
cd smart-pattern-backtester
pip install -r requirements.txt
