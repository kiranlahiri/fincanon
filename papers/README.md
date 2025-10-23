# FinCanon Papers Directory

This directory contains the finance research papers that power the RAG knowledge base.

## Directory Structure

```
papers/
├── asset_pricing/          # CAPM, APT, factor models, options pricing
├── portfolio_theory/       # Markowitz, optimization, diversification
├── risk_management/        # VaR, ARCH/GARCH, volatility modeling
├── behavioral_finance/     # Prospect theory, biases, anomalies
├── market_efficiency/      # EMH, momentum, market anomalies
└── papers_registry.json    # Metadata catalog of all papers
```

## Current Papers

### Already Ingested (3 papers)
- ✅ Markowitz (1952) - Portfolio Selection
- ✅ Sharpe (1964) - CAPM
- ✅ Fama & French (1992) - Three-Factor Model

### Ready to Add (8 papers)
Add these PDFs to the appropriate category folders:

**Asset Pricing:**
- `black_scholes_1973.pdf` → papers/asset_pricing/
- `merton_1973.pdf` → papers/asset_pricing/
- `ross_1976.pdf` → papers/asset_pricing/
- `carhart_1997.pdf` → papers/asset_pricing/

**Market Efficiency:**
- `fama_1970.pdf` → papers/market_efficiency/
- `jegadeesh_titman_1993.pdf` → papers/market_efficiency/

**Behavioral Finance:**
- `kahneman_tversky_1979.pdf` → papers/behavioral_finance/

**Risk Management:**
- `engle_1982.pdf` → papers/risk_management/

## How to Add New Papers

### Step 1: Download PDFs
Download the papers from academic sources (JSTOR, SSRN, Google Scholar, etc.)

### Step 2: Place PDFs in Category Folders
Copy each PDF to its appropriate category folder based on the filename in `papers_registry.json`

### Step 3: Run the Ingestion Script
```bash
# View current status
python ingest_papers.py --list

# Ingest all new papers
python ingest_papers.py

# Force re-ingestion of all papers
python ingest_papers.py --force
```

### Step 4: Verify
The script will:
- ✅ Ingest new papers into Qdrant
- ⏭️ Skip papers already ingested
- ❌ Report missing PDFs or errors
- 💾 Update `papers_registry.json` automatically

## Adding Custom Papers

To add a paper not in the registry:

1. Add an entry to `papers_registry.json`:
```json
{
  "id": "author_year",
  "filename": "your_paper.pdf",
  "category": "asset_pricing",
  "title": "Full Paper Title",
  "authors": ["First Author", "Second Author"],
  "year": 2020,
  "journal": "Journal Name",
  "key_concepts": ["concept1", "concept2"],
  "ingested": false
}
```

2. Place the PDF in `papers/{category}/your_paper.pdf`

3. Run `python ingest_papers.py`

## Where to Find Papers

### Academic Databases
- **JSTOR**: https://www.jstor.org/ (requires institutional access)
- **SSRN**: https://www.ssrn.com/ (many papers free)
- **Google Scholar**: https://scholar.google.com/ (links to paper sources)
- **NBER**: https://www.nber.org/ (working papers)

### Author Websites
Many authors post PDFs on their university websites

### Tips
- Search for "[Author] [Year] [Title] PDF"
- Look for working paper versions if journal version is paywalled
- Check author's personal website or university faculty page

## Registry Schema

Each paper entry contains:
- `id`: Unique identifier (author_year format)
- `filename`: PDF filename in the category folder
- `category`: One of: asset_pricing, portfolio_theory, risk_management, behavioral_finance, market_efficiency
- `title`: Full paper title
- `authors`: Array of author names
- `year`: Publication year
- `journal`: Journal or publication venue
- `key_concepts`: Tags for main concepts covered
- `ingested`: Boolean - has this been ingested into Qdrant?

## Troubleshooting

**"File not found" error:**
- Make sure PDF filename matches exactly (case-sensitive)
- Check PDF is in correct category subfolder

**"Already ingested" message:**
- Normal! Papers already in Qdrant are skipped
- Use `--force` flag to re-ingest if needed

**Ingestion fails:**
- Check PDF is valid and not corrupted
- Ensure Qdrant is running on localhost:6333
- Verify OpenAI API key is set

## Next Steps

After ingesting papers:
1. Restart your backend to use the expanded knowledge base
2. Try queries that reference the new papers
3. Monitor which papers are most frequently cited in answers
