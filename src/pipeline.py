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
   # loader = PyMuPDFLoader(pdf_path)
   # docs = loader.load()


    loader = UnstructuredPDFLoader(pdf_path)
    docs = loader.load()

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=250,
    separators=["\n\n", "\n", " ", ""]
)
    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata = {"title": doc_title, "page": chunk.metadata.get("page", None)}

    # 3. Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # 4. Qdrant client
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

def query_fincanon(query: str, k: int = 3):
    """Query Qdrant for relevant chunks."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    qdrant = QdrantVectorStore(
        QdrantClient(QDRANT_URL),
        COLLECTION_NAME,
        embeddings
    )
    results = qdrant.similarity_search(query, k=k)
    print("🔎 Query results:")
    for i, res in enumerate(results, start=1):
        print(f"\nResult {i}:")
        print(res.page_content[:300], "...")
        print(f"(Metadata: {res.metadata})")


def build_qa_chain():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    client = QdrantClient("http://localhost:6333")

    # Create retriever
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name="fincanon_papers",
        embedding=embeddings
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 15})

    # Custom prompt
    custom_prompt = PromptTemplate(
        template="""You are a financial research assistant.
Use the provided context from canonical finance papers to answer the question clearly.
If the context is relevant but indirect, explain the link in your own words.
If there is no relevant context at all, say you cannot answer.

Context:
{context}

Question: {question}
Answer:""",
        input_variables=["context", "question"],
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
