from pipeline import ingest_pdf, query_fincanon, build_qa_chain

# Ingest a PDF
ingest_pdf("markowitz_JF.pdf", "Portfolio Selection")

# Run a test query
query_fincanon("What is the best way to construct a portfolio?")

if __name__ == "__main__":
    ingest_pdf("markowitz_JF.pdf", "Portfolio Selection")
    qa = build_qa_chain()
    query = "What is the best way to construct a portfolio?"
    result = qa.invoke({"query": query})

    print("🔎 Question:", query)
    print("\n📖 Answer:", result["result"])
    print("\n📚 Sources:")
    for doc in result["source_documents"]:
        print("-", doc.metadata)


