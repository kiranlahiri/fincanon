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
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from typing import List
from langchain_core.documents import Document



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

    # Check if collection exists
    try:
        qdrant_client.get_collection("fincanon_papers")
        collection_exists = True
    except:
        collection_exists = False

    if collection_exists:
        # Add to existing collection
        qdrant = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            url="http://localhost:6333",
            collection_name="fincanon_papers"
        )
        print(f"Adding {len(chunks)} chunks to existing collection...")
        try:
            qdrant.add_documents(chunks)
            print(f"✅ Successfully added {len(chunks)} chunks")
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            raise
    else:
        # Create new collection
        print(f"Creating new collection with {len(chunks)} chunks...")
        try:
            qdrant = QdrantVectorStore.from_documents(
                chunks,
                embeddings,
                url="http://localhost:6333",
                collection_name="fincanon_papers"
            )
            print(f"✅ Successfully created collection with {len(chunks)} chunks")
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            raise

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

    # DEBUG: Print all retrieved documents
    print("\n" + "="*80)
    print(f"DEBUG: Retrieved {len(result['source_documents'])} documents for query: '{query}'")
    print("="*80)
    for i, doc in enumerate(result["source_documents"], 1):
        print(f"\n[{i}] {doc.metadata.get('title', 'Unknown')} (Page {doc.metadata.get('page', '?')})")
        print(f"    Content preview: {doc.page_content[:150]}...")
    print("\n" + "="*80 + "\n")

    # Extract answer and format sources
    answer = result["result"]
    sources = []
    for doc in result["source_documents"][:k]:
        sources.append({
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "metadata": doc.metadata
        })

    return answer, sources


def expand_query_with_terminology(query: str) -> list:
    """Generate multiple query variations to bridge modern/historical terminology.

    This helps retrieve papers that use older terminology (e.g., Markowitz's "efficient set")
    when users ask questions with modern terms (e.g., "efficient frontier").

    Returns a list of query strings, starting with the original.
    """
    query_variations = [query]  # Always include original query

    # Static mapping of modern terms to historical equivalents used in seminal papers
    term_replacements = {
        "efficient frontier": ["efficient set", "E-V efficient combinations", "mean-variance frontier"],
        "mean-variance": ["E-V analysis", "expected return and variance"],
        "sharpe ratio": ["reward-to-variability ratio", "risk-adjusted performance"],
        "optimal portfolio": ["efficient portfolio", "optimal E-V combination"],
        "diversification": ["portfolio selection", "spreading of risk"],
        "alpha": ["excess return", "abnormal return"],
        "beta": ["systematic risk", "market sensitivity"],
        "capm": ["capital asset pricing", "market model"],
    }

    # Generate variations by replacing modern terms with historical ones
    query_lower = query.lower()
    for modern_term, historical_terms in term_replacements.items():
        if modern_term in query_lower:
            # Add variations with each historical term
            for historical_term in historical_terms[:2]:  # Limit to 2 historical terms per modern term
                variation = query_lower.replace(modern_term, historical_term)
                query_variations.append(variation)
            break  # Only expand one concept to keep list manageable (3 queries max)

    return query_variations


class MultiQueryRetriever(BaseRetriever):
    """Custom retriever that expands queries with historical terminology."""

    vectorstore: QdrantVectorStore
    base_retriever: BaseRetriever

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, vectorstore, **kwargs):
        base_retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 10,           # Get 10 chunks per query variation
                "fetch_k": 40,
                "lambda_mult": 0.8
            }
        )
        super().__init__(vectorstore=vectorstore, base_retriever=base_retriever, **kwargs)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """Retrieve documents using query expansion for historical terminology."""
        # Generate query variations
        query_variations = expand_query_with_terminology(query)

        print(f"\n🔍 Query expansion: {len(query_variations)} variations")
        for i, var in enumerate(query_variations):
            print(f"  [{i+1}] {var}")

        # Retrieve documents for each query variation
        all_docs = []
        seen_content = set()  # Track unique chunks by content hash

        for query_var in query_variations:
            docs = self.base_retriever.get_relevant_documents(query_var)
            for doc in docs:
                # Deduplicate by content hash
                content_hash = hash(doc.page_content[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)

        # Return top 15 unique documents
        return all_docs[:15]


def build_qa_chain(portfolio_context: dict = None):
    """Build a QA chain with optional portfolio context.

    Args:
        portfolio_context: Optional dict with portfolio metrics to enhance answers
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    client = QdrantClient("http://localhost:6333")

    # Create vectorstore
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name="fincanon_papers",
        embedding=embeddings
    )

    # Use custom multi-query retriever with terminology expansion
    retriever = MultiQueryRetriever(vectorstore)

    # Build portfolio context string if provided
    portfolio_info = ""
    if portfolio_context:
        # Extract current portfolio metrics
        current_return = portfolio_context.get('portfolio_return_annual', 0)
        current_vol = portfolio_context.get('portfolio_vol_annual', 0)
        current_sharpe = portfolio_context.get('portfolio_sharpe_annual', 0)

        # Extract optimal portfolios if available
        optimal = portfolio_context.get('optimal_portfolios', {})
        max_sharpe = optimal.get('max_sharpe', {})
        min_variance = optimal.get('min_variance', {})

        # Build comparison string
        comparison_info = ""
        if max_sharpe and min_variance:
            sharpe_diff = max_sharpe.get('sharpe', 0) - current_sharpe
            vol_diff = current_vol - min_variance.get('volatility', 0)

            comparison_info = f"""

OPTIMAL PORTFOLIOS (for comparison):
- Maximum Sharpe Portfolio:
  * Return: {max_sharpe.get('return', 0)*100:.2f}%
  * Volatility: {max_sharpe.get('volatility', 0)*100:.2f}%
  * Sharpe Ratio: {max_sharpe.get('sharpe', 0):.3f}
  * Top weights: {', '.join([f"{asset}: {weight*100:.1f}%" for asset, weight in zip(portfolio_context.get('asset_means', {}).keys(), max_sharpe.get('weights', [])) if weight > 0.05][:3])}

- Minimum Variance Portfolio:
  * Return: {min_variance.get('return', 0)*100:.2f}%
  * Volatility: {min_variance.get('volatility', 0)*100:.2f}%
  * Sharpe Ratio: {min_variance.get('sharpe', 0):.3f}
  * Top weights: {', '.join([f"{asset}: {weight*100:.1f}%" for asset, weight in zip(portfolio_context.get('asset_means', {}).keys(), min_variance.get('weights', [])) if weight > 0.05][:3])}

COMPARISON TO OPTIMAL:
- Your Sharpe ({current_sharpe:.3f}) vs Max Sharpe ({max_sharpe.get('sharpe', 0):.3f}): Gap of {sharpe_diff:.3f}
- Your Volatility ({current_vol*100:.2f}%) vs Min Variance ({min_variance.get('volatility', 0)*100:.2f}%): Difference of {vol_diff*100:.2f}%
- Your portfolio {"lies on" if abs(sharpe_diff) < 0.1 else "is below"} the efficient frontier
"""

        portfolio_info = f"""

USER'S PORTFOLIO DATA:
- Annual Return: {current_return*100:.2f}%
- Annual Volatility: {current_vol*100:.2f}%
- Annual Sharpe Ratio: {current_sharpe:.3f}
- Maximum Drawdown: {portfolio_context.get('max_drawdown', 0)*100:.2f}%
- Sortino Ratio: {portfolio_context.get('sortino_ratio_annual', 0):.3f}
- Diversification Ratio: {portfolio_context.get('diversification_ratio', 0):.3f}
- Asset Composition: {', '.join([f"{asset}" for asset in portfolio_context.get('asset_means', {}).keys()])}
{comparison_info}
When answering, relate the theoretical concepts from the papers to the user's specific portfolio metrics and optimal portfolios above.
Use the comparison data to provide specific, actionable insights about how the user's portfolio performs relative to the efficient frontier.
"""

    # Custom prompt with optional portfolio context
    custom_prompt = PromptTemplate(
        template="""You are a finance research assistant specializing in portfolio theory. Your answers must be grounded in the research papers provided below.

CRITICAL RULES - Read Carefully:

1. CITATION SOURCES:
   - You may ONLY cite papers that appear in the "Context from Research Papers" section below
   - Check the context carefully - many relevant papers ARE provided
   - Do NOT cite papers from your general knowledge (e.g., Fishburn, Sortino) unless they appear in the context

2. HOW TO USE THE CONTEXT:
   - If papers in the context relate to the question, cite them and use their content
   - You can combine information from the papers with general finance knowledge
   - Be clear about what comes from the papers vs. general knowledge
   - Example: "Fama and French (1992) critique the CAPM model. The three-factor model they developed adds size and value factors..."

3. WHEN PAPERS CITE OTHER WORKS:
   - You may mention them but clarify: "as discussed in [Paper]" or "as cited by [Author]"

4. IF TRULY NO RELEVANT PAPERS:
   - Only if NONE of the retrieved papers relate to the question, then say the topic isn't covered
   - Then provide a helpful answer using general knowledge without citations

When answering:
- Answer the specific question asked directly and concisely
- Use concepts from the provided papers when relevant, citing them properly
- If the question is outside the scope of the provided papers, answer with general knowledge but WITHOUT fake citations
- Do NOT provide unsolicited recommendations or suggest the user's portfolio needs fixing
- When comparing to theoretical benchmarks, state facts and implications without judgmental language
- Be analytical and insightful, not verbose or prescriptive

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
