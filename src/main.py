import pandas as pd

from pipeline import ingest_pdf, query_fincanon, build_qa_chain
from metrics import analyze_portfolio


# NOTE: Paper ingestion has moved to the batch script!
# To ingest papers, use: python ../ingest_papers.py
# See papers/README.md for instructions

# Example: Test a query (assumes papers are already ingested)
print("="*60)
print("Testing RAG Query")
print("="*60 + "\n")

answer, sources = query_fincanon("What is the best way to construct a portfolio?", k=3)
print("🔎 Question: What is the best way to construct a portfolio?")
print(f"\n📖 Answer: {answer}")
print(f"\n📚 Sources ({len(sources)} documents):")
for i, source in enumerate(sources, 1):
    print(f"\n  Source {i}:")
    print(f"    Page: {source['metadata'].get('page')}")
    print(f"    Title: {source['metadata'].get('title')}")
    print(f"    Content: {source['content'][:100]}...")



if __name__ == "__main__":
   # papers = [("markowitz_JF.pdf", "Portfolio Selection"), ("Sharpe_1964.pdf","Capital Asset Pricing Model"),("FAMA_FRENCH.pdf","The Cross-Section of Expected Stock Returns")]

   # for file_path, title in papers:
   #     ingest_pdf(file_path, title)
   # 
   # qa = build_qa_chain()
   # query = "How do Fama-French’s factors extend CAPM?"
   # result = qa.invoke({"query": query})

   # print("🔎 Question:", query)
   # print("\n📖 Answer:", result["result"])
   # print("\n📚 Sources:")
   # for doc in result["source_documents"]:
   #     print("-", doc.metadata)

    df = pd.read_csv("../data/sample_portfolio.csv", index_col=0, parse_dates=True)




    results_equal = analyze_portfolio(df)
    print("\n=== Equal-Weight Portfolio ===")
    for k, v in results_equal.items():
        print(f"{k}: {v}")

    # Example 2: Custom-weight portfolio
    # 50% AAPL, 30% MSFT, 20% SPY
    custom_weights = [0.5, 0.3, 0.2]
    results_custom = analyze_portfolio(df, weights=custom_weights)
    print("\n=== Custom-Weight Portfolio (50/30/20) ===")
    for k, v in results_custom.items():
        print(f"{k}: {v}")
    #print(results)

