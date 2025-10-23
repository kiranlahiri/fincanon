from langchain_community.document_loaders import UnstructuredPDFLoader

# Test each PDF to see what metadata keys are present
pdfs = [
    ("markowitz_JF.pdf", "Markowitz"),
    ("Sharpe_1964.pdf", "Sharpe"),
    ("FAMA_FRENCH.pdf", "Fama-French")
]

for pdf_path, name in pdfs:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

    loader = UnstructuredPDFLoader(f"src/{pdf_path}")
    docs = loader.load()

    print(f"Total documents loaded: {len(docs)}")

    # Show metadata from first few docs
    for i, doc in enumerate(docs[:3]):
        print(f"\nDocument {i+1} metadata:")
        print(f"  Keys: {list(doc.metadata.keys())}")
        print(f"  Full metadata: {doc.metadata}")
        print(f"  Content preview: {doc.page_content[:100]}...")
