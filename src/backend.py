from fastapi import FastAPI, UploadFile, File
import pandas as pd
from metrics import analyze_portfolio
from pipeline import query_fincanon 

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (React on localhost:3000) to talk to backend (FastAPI on localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FinCanon backend 🚀"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Accepts a CSV file upload (portfolio data),
    computes metrics using analyze_portfolio,
    and returns the results as JSON.
    """
    # Read CSV into DataFrame
    df = pd.read_csv(file.file, index_col=0, parse_dates=True)

    # Compute portfolio metrics
    results = analyze_portfolio(df)

    return results

@app.post("/query")
async def query(payload: dict):
    """
    Accepts a question string from the frontend, queries the RAG pipeline,
    and returns an answer and the list of sources.
    """
    question = payload["question"]
    answer, sources = query_fincanon(question)
    return {"answer": answer, "sources": sources}
