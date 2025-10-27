# FinCanon

**A portfolio analysis tool that combines quantitative metrics with RAG-powered insights from classic finance literature.**

🔗 **Live Demo:** [fincanon.vercel.app](https://fincanon.vercel.app)

---

## Overview

FinCanon is a full-stack web application that analyzes investment portfolios using advanced financial metrics and provides AI-powered insights grounded in academic research. Upload your portfolio data to get instant analysis including Sharpe ratio, maximum drawdown, efficient frontier detection, and rolling performance charts. Ask questions about your portfolio and receive answers backed by seminal finance papers from Markowitz, Sharpe, Fama, Black-Scholes, and others.

### Key Features

- **📊 Quantitative Analysis**: Calculate key portfolio metrics including:
  - Sharpe Ratio (overall and rolling 90-day)
  - Maximum Drawdown
  - Volatility (annualized)
  - Expected Return
  - Sortino Ratio
  - Efficient Frontier Detection

- **📈 Interactive Visualizations**:
  - Time-series charts for rolling Sharpe ratio and drawdown
  - Portfolio and asset-level performance views
  - Quarterly windowed metrics

- **🤖 RAG-Powered Q&A**: Ask questions about your portfolio and receive insights powered by:
  - 10 embedded seminal finance papers
  - Retrieval-Augmented Generation (RAG) using LangChain
  - Portfolio-aware context injection
  - Source citations from academic literature

- **🎯 Efficient Frontier Analysis**: Automatically detects if your portfolio is on the efficient frontier

---

## Tech Stack

### Frontend
- **React** - UI framework
- **Recharts** - Data visualization
- **Axios** - API requests

### Backend
- **FastAPI** - REST API framework
- **Python** - Core language
- **pandas & NumPy** - Data processing and financial calculations
- **SciPy** - Statistical computations

### AI/ML
- **LangChain** - RAG orchestration
- **OpenAI** - Embeddings (text-embedding-3-large) and LLM (GPT-4)
- **Qdrant** - Vector database for semantic search

### Deployment
- **Vercel** - Frontend hosting
- **Railway** - Backend hosting
- **Qdrant Cloud** - Managed vector database

---

## Architecture

```
┌─────────────┐
│   React     │ (Frontend - Vercel)
│   Frontend  │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   FastAPI   │ (Backend - Railway)
│   Backend   │
└──────┬──────┘
       │
       ├─────────► pandas/NumPy (Portfolio Metrics)
       │
       └─────────► LangChain RAG Pipeline
                         │
                         ├─► OpenAI (Embeddings & LLM)
                         │
                         └─► Qdrant Cloud (Vector DB)
```

**Data Flow:**
1. User uploads CSV portfolio data
2. Backend calculates quantitative metrics (Sharpe, drawdown, etc.)
3. Frontend displays interactive charts and metrics
4. User asks questions via chat interface
5. RAG system retrieves relevant chunks from finance papers
6. LLM generates answer using portfolio context + retrieved research
7. Answer with sources returned to frontend

---

## Embedded Research Papers

The RAG system queries the following seminal finance papers:

- **Markowitz (1952)** - Portfolio Selection
- **Sharpe (1964)** - Capital Asset Pricing Model
- **Fama (1970)** - Efficient Capital Markets
- **Black-Scholes (1973)** - Options Pricing
- **Merton (1973)** - Intertemporal Capital Asset Pricing Model
- **Ross (1976)** - Arbitrage Theory of Capital Asset Pricing
- **Kahneman & Tversky (1979)** - Prospect Theory
- **Engle (1982)** - Autoregressive Conditional Heteroskedasticity (ARCH)
- **Fama & French (1993)** - Common Risk Factors in Stock Returns
- **Jegadeesh & Titman (1993)** - Returns to Buying Winners and Selling Losers

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- OpenAI API key
- Qdrant instance (local or cloud)

### Local Development

#### 1. Clone the repository
```bash
git clone https://github.com/kiranlahiri/fincanon.git
cd fincanon
```

#### 2. Backend Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your-key-here
# QDRANT_URL=http://localhost:6333  # Or your Qdrant Cloud URL
# QDRANT_API_KEY=  # Leave empty for local Qdrant
```

#### 3. Start Qdrant (Local Option)
```bash
docker run -d \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

#### 4. Ingest Finance Papers
```bash
python -c "
from src.pipeline import ingest_pdf
import glob

papers = glob.glob('papers/**/*.pdf', recursive=True)
for pdf_path in papers:
    doc_title = pdf_path.split('/')[-1].replace('.pdf', '')
    ingest_pdf(pdf_path, doc_title)
    print(f'✓ Ingested {doc_title}')
"
```

#### 5. Start Backend
```bash
uvicorn src.backend:app --reload --port 8000
```

#### 6. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit .env:
# REACT_APP_API_URL=http://localhost:8000

# Start development server
npm start
```

Visit `http://localhost:3000` to use the application locally.

---

## CSV Input Format

Upload a CSV file with the following format:

```csv
Date,AAPL,MSFT,GOOGL,AMZN
Weights,0.25,0.25,0.25,0.25
2024-01-02,0.0123,-0.0045,0.0078,0.0156
2024-01-03,-0.0034,0.0089,0.0023,-0.0012
...
```

**Requirements:**
- First row: Header with `Date` and asset tickers
- Second row: `Weights` and corresponding portfolio weights (must sum to 1.0)
- Subsequent rows: Dates and daily returns as decimals (e.g., 0.0123 = 1.23% return)

**Example CSV files** are available in the `examples/` directory.

---

## Deployment

### Production Deployment

The application is deployed with the following services:

- **Frontend**: Vercel (auto-deploys from `main` branch)
- **Backend**: Railway (auto-deploys from `main` branch)
- **Vector DB**: Qdrant Cloud (managed service)

### Environment Variables

**Backend (Railway):**
```bash
OPENAI_API_KEY=your-openai-key
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
FRONTEND_URL=https://fincanon.vercel.app
```

**Frontend (Vercel):**
```bash
REACT_APP_API_URL=https://your-backend.up.railway.app
```

---

## Project Structure

```
fincanon/
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Main component with portfolio analysis & chat
│   │   └── index.js
│   ├── public/
│   └── package.json
├── src/                   # Python backend
│   ├── backend.py         # FastAPI endpoints (/analyze, /query)
│   ├── metrics.py         # Portfolio metrics calculations
│   └── pipeline.py        # RAG pipeline (ingestion & querying)
├── papers/                # Finance research papers (PDFs)
│   ├── portfolio_theory/
│   ├── asset_pricing/
│   ├── market_efficiency/
│   ├── behavioral_finance/
│   └── risk_management/
├── examples/              # Example portfolio CSV files
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment config
└── README.md
```

---

## API Endpoints

### `POST /analyze`
Analyzes portfolio data and returns metrics.

**Request:** Multipart form data with CSV file

**Response:**
```json
{
  "overall_metrics": {
    "sharpe_ratio": 1.238,
    "max_drawdown": -0.1262,
    "volatility": 0.1845,
    "expected_return": 0.1107,
    "sortino_ratio": 1.789,
    "efficient_frontier_status": "on_frontier"
  },
  "quarterly_metrics": [...],
  "asset_metrics": [...],
  "rolling_sharpe": [...],
  "drawdown_series": [...]
}
```

### `POST /query`
Queries the RAG system with a question.

**Request:**
```json
{
  "question": "What is portfolio diversification?",
  "portfolio_metrics": { ... }  // Optional
}
```

**Response:**
```json
{
  "answer": "Portfolio diversification is...",
  "sources": [
    {
      "content": "...",
      "metadata": {
        "title": "markowitz_JF",
        "page": 3
      }
    }
  ]
}
```

---

## Future Enhancements

- [ ] **Interactive Portfolio Builder**: Ticker search, weight sliders, automatic data fetching from Yahoo Finance
- [ ] **Additional Metrics**: Value at Risk (VaR), Conditional VaR, Beta calculation
- [ ] **Export Functionality**: PDF reports, downloadable charts
- [ ] **Portfolio Comparison**: Compare multiple portfolios side-by-side
- [ ] **Historical Backtesting**: Simulate portfolio performance over different time periods
- [ ] **More Research Papers**: Expand knowledge base with additional finance literature
- [ ] **User Accounts**: Save and track multiple portfolios over time

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

MIT License - see LICENSE file for details

---

## Contact

**Kiran Lahiri**
- GitHub: [@kiranlahiri](https://github.com/kiranlahiri)
- Website: [kiranlahiri.github.io](https://kiranlahiri.github.io)

---

## Acknowledgments

- Finance papers from their respective authors and publishers
- Built with LangChain, OpenAI, and Qdrant
- Inspired by modern portfolio theory and quantitative finance research
