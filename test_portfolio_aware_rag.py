"""Test portfolio-aware RAG queries"""
import sys
sys.path.append('src')

from pipeline import query_fincanon

# Sample portfolio metrics (like what frontend sends)
sample_metrics = {
    "portfolio_return_annual": 0.08,
    "portfolio_vol_annual": 0.15,
    "portfolio_sharpe_annual": 0.53,
    "asset_means": {
        "AAPL": 0.0003,
        "MSFT": 0.0002,
        "SPY": 0.0001
    },
    "asset_vols": {
        "AAPL": 0.012,
        "MSFT": 0.010,
        "SPY": 0.008
    }
}

print("="*70)
print("TEST 1: Query WITHOUT portfolio context")
print("="*70)

question1 = "What is the Sharpe ratio and why is it important?"
print(f"\nQuestion: {question1}\n")

answer1, sources1 = query_fincanon(question1, k=2, portfolio_context=None)
print(f"Answer: {answer1}\n")
print(f"Sources: {len(sources1)} documents")

print("\n" + "="*70)
print("TEST 2: Query WITH portfolio context (portfolio-aware)")
print("="*70)

question2 = "How does my portfolio's Sharpe ratio compare to theoretical expectations?"
print(f"\nQuestion: {question2}\n")
print(f"Portfolio Context:")
print(f"  - Annual Return: {sample_metrics['portfolio_return_annual']:.2%}")
print(f"  - Annual Volatility: {sample_metrics['portfolio_vol_annual']:.2%}")
print(f"  - Annual Sharpe: {sample_metrics['portfolio_sharpe_annual']:.2f}\n")

answer2, sources2 = query_fincanon(question2, k=2, portfolio_context=sample_metrics)
print(f"Answer: {answer2}\n")
print(f"Sources: {len(sources2)} documents")

print("\n" + "="*70)
print("TEST 3: Portfolio diversification question with context")
print("="*70)

question3 = "Should I diversify more given my current volatility?"
print(f"\nQuestion: {question3}\n")

answer3, sources3 = query_fincanon(question3, k=2, portfolio_context=sample_metrics)
print(f"Answer: {answer3}\n")
print(f"Sources: {len(sources3)} documents")

print("\n" + "="*70)
print("✅ Portfolio-aware RAG tests complete!")
print("="*70)
