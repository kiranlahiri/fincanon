import os
#from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import UnstructuredPDFLoader



# --- CONFIG ---
COLLECTION_NAME = "fincanon_papers"
QDRANT_URL = "http://localhost:6333"  # or your Qdrant Cloud URL

# Make sure your OPENAI_API_KEY is set as env var
# export OPENAI_API_KEY="sk-..."

def ingest_pdf(pdf_path: str, doc_title: str):
    """Load, chunk, embed, and store a PDF into Qdrant."""
    # 1. Load PDF
    # Option A: Use UnstructuredPDFLoader with mode='elements' to get page_number
    loader = UnstructuredPDFLoader(pdf_path, mode="elements")
    docs = loader.load()

    # Option B (alternative): Use PyMuPDFLoader which extracts page numbers as 'page' (0-indexed)
    # from langchain_community.document_loaders import PyMuPDFLoader
    # loader = PyMuPDFLoader(pdf_path)
    # docs = loader.load()

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=250,
    separators=["\n\n", "\n", " ", ""]
)
    chunks = splitter.split_documents(docs)

    # 3. Normalize metadata to extract page numbers consistently
    for chunk in chunks:
        # UnstructuredPDFLoader with mode='elements' uses 'page_number' (1-indexed)
        # PyMuPDFLoader uses 'page' (0-indexed)
        page_num = chunk.metadata.get("page_number") or chunk.metadata.get("page")

        # Convert to 1-indexed if using PyMuPDFLoader (which is 0-indexed)
        if "page" in chunk.metadata and "page_number" not in chunk.metadata:
            page_num = page_num + 1 if page_num is not None else None

        chunk.metadata = {
            "title": doc_title,
            "page": page_num,
            "source": chunk.metadata.get("source", pdf_path)
        }

    # 4. Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # 5. Qdrant client
    qdrant_client = QdrantClient(QDRANT_URL)
    try:
        qdrant = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            url="http://localhost:6333",
            collection_name="fincanon_papers"
        )
        qdrant.add_documents(chunks)
    except:
        qdrant = QdrantVectorStore.from_documents(
            chunks,
            embeddings,
            url="http://localhost:6333",
            collection_name="fincanon_papers"
        )

    print(f"✅ Ingested {len(chunks)} chunks from {doc_title} into Qdrant")

def query_fincanon(query: str, k: int = 3, portfolio_context: dict = None):
    """Query Qdrant for relevant chunks and generate an answer using LLM.

    Args:
        query: The user's question
        k: Number of source documents to return
        portfolio_context: Optional dictionary containing portfolio metrics
    """
    # Build the QA chain with portfolio context
    qa_chain = build_qa_chain(portfolio_context=portfolio_context)

    # Get answer with sources
    result = qa_chain.invoke({"query": query})

    # Extract answer and format sources
    answer = result["result"]
    sources = []
    for doc in result["source_documents"][:k]:
        sources.append({
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "metadata": doc.metadata
        })

    return answer, sources


def build_qa_chain(portfolio_context: dict = None):
    """Build a QA chain with optional portfolio context.

    Args:
        portfolio_context: Optional dict with portfolio metrics to enhance answers
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    client = QdrantClient("http://localhost:6333")

    # Create retriever with MMR for diverse multi-paper retrieval
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name="fincanon_papers",
        embedding=embeddings
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance for diversity
        search_kwargs={
            "k": 15,           # Return 15 diverse chunks
            "fetch_k": 50,     # Initially fetch 50 candidates
            "lambda_mult": 0.7 # Balance: 0.7 = more relevance, 0.5 = balanced, 0.3 = more diversity
        }
    )

    # Build portfolio context string if provided
    portfolio_info = ""
    if portfolio_context:
        portfolio_info = f"""

USER'S PORTFOLIO DATA:
- Annual Return: {portfolio_context.get('portfolio_return_annual', 'N/A'):.4f} ({portfolio_context.get('portfolio_return_annual', 0)*100:.2f}%)
- Annual Volatility: {portfolio_context.get('portfolio_vol_annual', 'N/A'):.4f} ({portfolio_context.get('portfolio_vol_annual', 0)*100:.2f}%)
- Annual Sharpe Ratio: {portfolio_context.get('portfolio_sharpe_annual', 'N/A'):.4f}
- Asset Composition: {', '.join([f"{asset}: {val:.4f}" for asset, val in portfolio_context.get('asset_means', {}).items()])}

When answering, relate the theoretical concepts from the papers to the user's specific portfolio metrics above.
"""

    # Custom prompt with optional portfolio context
    custom_prompt = PromptTemplate(
        template="""You are a financial research assistant specializing in portfolio theory.
Use the provided context from canonical finance papers to answer the question clearly.
If the context is relevant but indirect, explain the link in your own words.
If there is no relevant context at all, say you cannot answer.
{portfolio_info}
Context from Research Papers:
{context}

Question: {question}
Answer:""",
        input_variables=["context", "question"],
        partial_variables={"portfolio_info": portfolio_info}
    )

    # Wrap retriever with GPT
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": custom_prompt},
        return_source_documents=True
    )
    return qa_chain
