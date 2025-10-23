#!/usr/bin/env python3
"""Test Tier 2 portfolio optimization"""
import sys
sys.path.insert(0, 'src')

import pandas as pd
from metrics import analyze_portfolio

# Load the diversified portfolio
df = pd.read_csv('data/diversified_portfolio.csv', index_col=0, parse_dates=True)

print("="*70)
print("TESTING TIER 2 METRICS - Portfolio Optimization")
print("="*70)
print(f"\nPortfolio: {', '.join(df.columns)}")

# Analyze with equal weights
results = analyze_portfolio(df)

print("\n" + "="*70)
print("CURRENT PORTFOLIO (Equal-Weighted)")
print("="*70)
print(f"Return:     {results['portfolio_return_annual']:.2%}")
print(f"Volatility: {results['portfolio_vol_annual']:.2%}")
print(f"Sharpe:     {results['portfolio_sharpe_annual']:.3f}")

print("\n" + "="*70)
print("OPTIMAL PORTFOLIOS")
print("="*70)

# Minimum Variance Portfolio
min_var = results['optimal_portfolios']['min_variance']
print("\n🔹 MINIMUM VARIANCE PORTFOLIO")
print(f"Return:     {min_var['return']:.2%}")
print(f"Volatility: {min_var['volatility']:.2%}")
print(f"Sharpe:     {min_var['sharpe']:.3f}")
print("\nWeights:")
for i, (asset, weight) in enumerate(zip(df.columns, min_var['weights'])):
    if weight > 0.01:  # Only show non-negligible weights
        print(f"  {asset}: {weight:.1%}")

# Maximum Sharpe Portfolio
max_sharpe = results['optimal_portfolios']['max_sharpe']
print("\n🔹 MAXIMUM SHARPE PORTFOLIO")
print(f"Return:     {max_sharpe['return']:.2%}")
print(f"Volatility: {max_sharpe['volatility']:.2%}")
print(f"Sharpe:     {max_sharpe['sharpe']:.3f}")
print("\nWeights:")
for i, (asset, weight) in enumerate(zip(df.columns, max_sharpe['weights'])):
    if weight > 0.01:
        print(f"  {asset}: {weight:.1%}")

# Efficient Frontier
print("\n" + "="*70)
print("EFFICIENT FRONTIER")
print("="*70)
print(f"\n{len(results['efficient_frontier'])} portfolios calculated")
print("\nSample points:")
for i in [0, len(results['efficient_frontier'])//2, -1]:
    point = results['efficient_frontier'][i]
    print(f"  Return: {point['return']:.2%}, Vol: {point['volatility']:.2%}")

print("\n" + "="*70)
print("✅ Tier 2 optimization complete!")
print("="*70 + "\n")
