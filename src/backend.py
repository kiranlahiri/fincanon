from fastapi import FastAPI, UploadFile, File
import pandas as pd
import numpy as np
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

    CSV format:
    - Row 1: Header with 'Date' and asset tickers
    - Row 2: 'Weights' and corresponding portfolio weights (must sum to 1.0)
    - Row 3+: Dates and daily returns (as decimals)
    """
    # Read CSV into DataFrame
    df = pd.read_csv(file.file, index_col=0, parse_dates=False)

    # Extract weights if present (second row with index='Weights')
    weights = None
    if 'Weights' in df.index:
        weights = df.loc['Weights'].values.astype(float)
        # Remove weights row from dataframe
        df = df.drop('Weights')

        # Validate weights sum to ~1.0
        weights_sum = weights.sum()
        if not np.isclose(weights_sum, 1.0, atol=0.01):
            return {"error": f"Weights must sum to 1.0 (got {weights_sum:.4f})"}

    # Convert index to datetime
    df.index = pd.to_datetime(df.index)

    # Compute portfolio metrics
    results = analyze_portfolio(df, weights=weights)

    return results

@app.post("/query")
async def query(payload: dict):
    """
    Accepts a question string from the frontend, queries the RAG pipeline,
    and returns an answer and the list of sources.

    Optionally accepts portfolio_metrics to provide portfolio-aware answers.
    """
    question = payload["question"]
    portfolio_metrics = payload.get("portfolio_metrics", None)

    answer, sources = query_fincanon(question, portfolio_context=portfolio_metrics)
    return {"answer": answer, "sources": sources}
