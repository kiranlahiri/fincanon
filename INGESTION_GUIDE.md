# Paper Ingestion Guide

## New Workflow (Current)

Papers are now organized in the `papers/` directory and ingested using the batch script.

### Step 1: Check Current Status
```bash
python ingest_papers.py --list
```

This shows:
- ✅ Papers already ingested
- ⏳ Papers waiting to be added
- 📁 Where to place each PDF

### Step 2: Add PDF Files

Place PDFs in category folders with exact filenames from registry:

```
papers/
├── asset_pricing/
│   ├── Sharpe_1964.pdf              ✅ Already here
│   ├── FAMA_FRENCH.pdf              ✅ Already here
│   ├── black_scholes_1973.pdf       ⏳ Add this
│   ├── merton_1973.pdf              ⏳ Add this
│   ├── ross_1976.pdf                ⏳ Add this
│   └── carhart_1997.pdf             ⏳ Add this
├── portfolio_theory/
│   └── markowitz_JF.pdf             ✅ Already here
├── behavioral_finance/
│   └── kahneman_tversky_1979.pdf    ⏳ Add this
├── market_efficiency/
│   ├── fama_1970.pdf                ⏳ Add this
│   └── jegadeesh_titman_1993.pdf    ⏳ Add this
└── risk_management/
    └── engle_1982.pdf               ⏳ Add this
```

### Step 3: Run Batch Ingestion
```bash
# Make sure Qdrant is running
docker ps  # or however you run Qdrant

# Ingest all new papers
.venv/bin/python ingest_papers.py
```

The script will:
- ✅ Ingest new papers automatically
- ⏭️ Skip papers already ingested
- ❌ Report which PDFs are missing
- 💾 Update the registry

### Step 4: Verify
```bash
# Check updated status
python ingest_papers.py --list
```

---

## Old Workflow (Deprecated)

❌ **Don't use `src/main.py` for ingestion anymore**

The old way was:
```python
# src/main.py (OLD - don't use)
papers = [("markowitz_JF.pdf", "Portfolio Selection"), ...]
for file_path, title in papers:
    ingest_pdf(file_path, title)
```

This is now replaced by the batch script.

---

## Quick Commands

```bash
# List papers and status
python ingest_papers.py --list

# Ingest new papers
.venv/bin/python ingest_papers.py

# Force re-ingest everything
.venv/bin/python ingest_papers.py --force

# Test queries
cd src && ../.venv/bin/python main.py
```

---

## Benefits of New System

✅ **Organized** - Papers sorted by category
✅ **Tracked** - Registry knows what's ingested
✅ **Batch** - Ingest many papers at once
✅ **Idempotent** - Won't re-ingest same paper
✅ **Extensible** - Easy to add new papers

---

## Troubleshooting

**"File not found"**
- Check filename matches registry exactly (case-sensitive)
- Ensure PDF is in correct category folder

**"Collection doesn't exist"**
- Qdrant not running or collection not created
- First ingestion creates the collection automatically

**"Already ingested"**
- Normal! Papers skip if already done
- Use `--force` to re-ingest

---

## Adding Custom Papers

Edit `papers/papers_registry.json` to add new papers not in the default list.

See `papers/README.md` for full instructions.
