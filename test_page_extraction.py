"""Test page number extraction after fix"""
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def test_page_extraction(pdf_path, doc_title):
    print(f"\n{'='*60}")
    print(f"Testing: {doc_title}")
    print('='*60)

    # Load with mode='elements'
    loader = UnstructuredPDFLoader(pdf_path, mode="elements")
    docs = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=250,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    # Normalize metadata
    for chunk in chunks:
        page_num = chunk.metadata.get("page_number") or chunk.metadata.get("page")

        if "page" in chunk.metadata and "page_number" not in chunk.metadata:
            page_num = page_num + 1 if page_num is not None else None

        chunk.metadata = {
            "title": doc_title,
            "page": page_num,
            "source": chunk.metadata.get("source", pdf_path)
        }

    print(f"Total chunks: {len(chunks)}")

    # Show page distribution
    page_counts = {}
    for chunk in chunks:
        page = chunk.metadata.get("page", "None")
        page_counts[page] = page_counts.get(page, 0) + 1

    print(f"\nPage distribution:")
    for page in sorted([p for p in page_counts.keys() if p != "None"]):
        print(f"  Page {page}: {page_counts[page]} chunks")

    if "None" in page_counts:
        print(f"  Page None: {page_counts['None']} chunks")

    # Show first 3 chunks with page numbers
    print(f"\nFirst 3 chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n  Chunk {i+1}:")
        print(f"    Page: {chunk.metadata.get('page')}")
        print(f"    Title: {chunk.metadata.get('title')}")
        print(f"    Content preview: {chunk.page_content[:80]}...")

# Test all three PDFs
pdfs = [
    ("src/markowitz_JF.pdf", "Portfolio Selection"),
    ("src/Sharpe_1964.pdf", "Capital Asset Pricing Model"),
    ("src/FAMA_FRENCH.pdf", "The Cross-Section of Expected Stock Returns")
]

for pdf_path, title in pdfs:
    test_page_extraction(pdf_path, title)

print("\n" + "="*60)
print("✅ Page extraction test complete!")
print("="*60)
