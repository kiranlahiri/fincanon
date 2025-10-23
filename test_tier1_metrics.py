#!/usr/bin/env python3
"""Test Tier 1 advanced metrics"""
import sys
sys.path.insert(0, 'src')

import pandas as pd
from metrics import analyze_portfolio

# Load the diversified portfolio
df = pd.read_csv('data/diversified_portfolio.csv', index_col=0, parse_dates=True)

print("="*70)
print("TESTING TIER 1 METRICS - Diversified Portfolio")
print("="*70)
print(f"\nPortfolio: {', '.join(df.columns)}")
print(f"Date Range: {df.index[0].date()} to {df.index[-1].date()}")
print(f"Trading Days: {len(df)}")

# Analyze with equal weights
results = analyze_portfolio(df)

print("\n" + "="*70)
print("PORTFOLIO METRICS")
print("="*70)

print("\n--- BASIC METRICS ---")
print(f"Annual Return:       {results['portfolio_return_annual']:.2%}")
print(f"Annual Volatility:   {results['portfolio_vol_annual']:.2%}")
print(f"Sharpe Ratio:        {results['portfolio_sharpe_annual']:.4f}")

print("\n--- TIER 1: ADVANCED RISK METRICS ---")
print(f"Maximum Drawdown:    {results['max_drawdown']:.2%}")
print(f"Sortino Ratio (Ann): {results['sortino_ratio_annual']:.4f}")
print(f"Beta vs SPY:         {results['beta']:.4f}" if not pd.isna(results['beta']) else "Beta vs SPY:         N/A (SPY not in portfolio)")
print(f"Diversification:     {results['diversification_ratio']:.4f}")

print("\n--- CORRELATION MATRIX (Top 3 Pairs) ---")
corr_df = pd.DataFrame(results['correlation_matrix'])
# Get upper triangle of correlation matrix
import numpy as np
mask = np.triu(np.ones_like(corr_df, dtype=bool), k=1)
corr_pairs = corr_df.where(mask).stack().sort_values(ascending=False)
for i, (pair, corr) in enumerate(corr_pairs.head(3).items()):
    print(f"{pair[0]}-{pair[1]}: {corr:.3f}")

print("\n--- ASSET-LEVEL STATS ---")
assets_df = pd.DataFrame({
    'Annual Return': {k: v*252 for k, v in results['asset_means'].items()},
    'Annual Vol': {k: v*np.sqrt(252) for k, v in results['asset_vols'].items()}
})
assets_df['Sharpe'] = assets_df['Annual Return'] / assets_df['Annual Vol']
print(assets_df.sort_values('Sharpe', ascending=False).to_string())

print("\n" + "="*70)
print("✅ Tier 1 metrics calculated successfully!")
print("="*70 + "\n")
