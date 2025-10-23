#!/usr/bin/env python3
"""
Download real portfolio data from Yahoo Finance
Requires: pip install yfinance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Date range: 2 years of data
end_date = datetime.now()
start_date = end_date - timedelta(days=730)  # ~2 years

print("="*70)
print("Downloading Portfolio Data from Yahoo Finance")
print("="*70)
print(f"Date Range: {start_date.date()} to {end_date.date()}\n")

# Portfolio 1: Diversified Multi-Asset
print("1. Downloading Diversified Portfolio...")
diversified_tickers = ['AAPL', 'MSFT', 'JNJ', 'JPM', 'XOM', 'AGG', 'GLD', 'VNQ']
diversified_data = yf.download(diversified_tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)
# Handle both single and multi-ticker downloads
if len(diversified_tickers) == 1:
    diversified_prices = diversified_data[['Close']]
else:
    diversified_prices = diversified_data['Close'] if 'Close' in diversified_data.columns else diversified_data
diversified_returns = diversified_prices.pct_change().dropna()
diversified_returns.to_csv('data/diversified_portfolio.csv')
print(f"   ✅ Saved: data/diversified_portfolio.csv ({len(diversified_returns)} days, {len(diversified_tickers)} assets)")

# Portfolio 2: Concentrated Tech
print("\n2. Downloading Tech Portfolio...")
tech_tickers = ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA']
tech_data = yf.download(tech_tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)
tech_prices = tech_data['Close'] if 'Close' in tech_data.columns else tech_data
tech_returns = tech_prices.pct_change().dropna()
tech_returns.to_csv('data/tech_portfolio.csv')
print(f"   ✅ Saved: data/tech_portfolio.csv ({len(tech_returns)} days, {len(tech_tickers)} assets)")

# Portfolio 3: Classic 60/40
print("\n3. Downloading 60/40 Portfolio...")
balanced_tickers = ['SPY', 'QQQ', 'IWM', 'AGG', 'TLT', 'LQD']
balanced_data = yf.download(balanced_tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)
balanced_prices = balanced_data['Close'] if 'Close' in balanced_data.columns else balanced_data
balanced_returns = balanced_prices.pct_change().dropna()
balanced_returns.to_csv('data/balanced_60_40.csv')
print(f"   ✅ Saved: data/balanced_60_40.csv ({len(balanced_returns)} days, {len(balanced_tickers)} assets)")

print("\n" + "="*70)
print("Summary")
print("="*70)
print("\nPortfolio Descriptions:")
print("\n📊 Diversified Portfolio (diversified_portfolio.csv):")
print("   - AAPL, MSFT: Tech")
print("   - JNJ: Healthcare")
print("   - JPM: Finance")
print("   - XOM: Energy")
print("   - AGG: Bonds")
print("   - GLD: Gold")
print("   - VNQ: Real Estate")
print("   → Tests: Good diversification, lower correlation")

print("\n💻 Tech Portfolio (tech_portfolio.csv):")
print("   - AAPL, MSFT, GOOGL, META, NVDA")
print("   → Tests: High correlation, concentration risk")

print("\n⚖️  60/40 Balanced (balanced_60_40.csv):")
print("   - SPY, QQQ, IWM: Stocks")
print("   - AGG, TLT, LQD: Bonds")
print("   → Tests: Classic allocation, stock-bond correlation")

print("\n✅ All portfolios downloaded successfully!")
print("="*70 + "\n")

# Show quick stats
print("Quick Preview - Diversified Portfolio:")
print(diversified_returns.tail())
print(f"\nAnnualized Returns:")
print((diversified_returns.mean() * 252).round(4))
print(f"\nAnnualized Volatility:")
print((diversified_returns.std() * (252**0.5)).round(4))
