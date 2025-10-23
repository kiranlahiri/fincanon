from langchain_community.document_loaders import UnstructuredPDFLoader
try:
    from langchain_community.document_loaders import PyMuPDFLoader
    PYMUPDF_AVAILABLE = True
except:
    PYMUPDF_AVAILABLE = False

print("="*60)
print("Option 1: UnstructuredPDFLoader with mode='elements'")
print("="*60)

loader = UnstructuredPDFLoader("src/markowitz_JF.pdf", mode="elements")
docs = loader.load()

print(f"Total documents: {len(docs)}")
print(f"\nFirst 5 documents metadata:")
for i, doc in enumerate(docs[:5]):
    print(f"\nDoc {i+1}:")
    print(f"  Metadata: {doc.metadata}")
    print(f"  Content preview: {doc.page_content[:80]}...")

if PYMUPDF_AVAILABLE:
    print("\n" + "="*60)
    print("Option 2: PyMuPDFLoader")
    print("="*60)

    loader = PyMuPDFLoader("src/markowitz_JF.pdf")
    docs = loader.load()

    print(f"Total documents: {len(docs)}")
    print(f"\nFirst 5 documents metadata:")
    for i, doc in enumerate(docs[:5]):
        print(f"\nDoc {i+1}:")
        print(f"  Metadata: {doc.metadata}")
        print(f"  Content preview: {doc.page_content[:80]}...")
else:
    print("\nPyMuPDFLoader not available")
