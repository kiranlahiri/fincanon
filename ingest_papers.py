#!/usr/bin/env python3
"""
Batch ingestion script for finance papers.
Reads from papers_registry.json and ingests all papers that haven't been ingested yet.
"""
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pipeline import ingest_pdf

def load_registry():
    """Load the papers registry."""
    registry_path = Path(__file__).parent / 'papers' / 'papers_registry.json'
    with open(registry_path, 'r') as f:
        return json.load(f)

def save_registry(registry):
    """Save the updated papers registry."""
    registry_path = Path(__file__).parent / 'papers' / 'papers_registry.json'
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)

def ingest_all_papers(force=False):
    """
    Ingest all papers from the registry.

    Args:
        force: If True, re-ingest papers even if already ingested
    """
    registry = load_registry()
    papers_dir = Path(__file__).parent / 'papers'

    total_papers = len(registry['papers'])
    ingested_count = 0
    skipped_count = 0
    error_count = 0

    print(f"\n{'='*70}")
    print(f"FinCanon Paper Ingestion")
    print(f"{'='*70}\n")
    print(f"Found {total_papers} papers in registry\n")

    for paper in registry['papers']:
        paper_id = paper['id']
        filename = paper['filename']
        category = paper['category']
        title = paper['title']
        already_ingested = paper.get('ingested', False)

        # Construct full path
        pdf_path = papers_dir / category / filename

        # Skip if already ingested (unless force)
        if already_ingested and not force:
            print(f"⏭️  SKIP: {title}")
            print(f"   Already ingested (use --force to re-ingest)")
            skipped_count += 1
            continue

        # Check if file exists
        if not pdf_path.exists():
            print(f"❌ ERROR: {title}")
            print(f"   File not found: {pdf_path}")
            print(f"   Please add the PDF to: papers/{category}/")
            error_count += 1
            continue

        # Ingest the paper
        print(f"📄 INGESTING: {title}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print(f"   Year: {paper['year']}")
        print(f"   Category: {category}")
        print(f"   File: {pdf_path}")

        try:
            ingest_pdf(str(pdf_path), title)
            paper['ingested'] = True
            ingested_count += 1
            print(f"   ✅ Success!\n")
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}\n")
            error_count += 1
            continue

    # Save updated registry
    save_registry(registry)

    # Print summary
    print(f"\n{'='*70}")
    print(f"Ingestion Summary")
    print(f"{'='*70}")
    print(f"✅ Successfully ingested: {ingested_count} papers")
    print(f"⏭️  Skipped (already done): {skipped_count} papers")
    print(f"❌ Errors: {error_count} papers")
    print(f"📚 Total in registry: {total_papers} papers")
    print(f"{'='*70}\n")

    if error_count > 0:
        print("⚠️  Some papers could not be ingested. Please check the errors above.")
        print("   Add missing PDFs to the appropriate category folders in papers/\n")

def list_papers():
    """List all papers in the registry with their status."""
    registry = load_registry()

    print(f"\n{'='*70}")
    print(f"Papers Registry")
    print(f"{'='*70}\n")

    categories = {}
    for paper in registry['papers']:
        cat = paper['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(paper)

    for category, papers in sorted(categories.items()):
        print(f"\n📁 {category.upper().replace('_', ' ')}")
        print(f"   {'-'*60}")
        for paper in papers:
            status = "✅" if paper.get('ingested', False) else "⏳"
            print(f"   {status} [{paper['year']}] {paper['title']}")
            print(f"      {', '.join(paper['authors'])}")
            if not paper.get('ingested', False):
                print(f"      📄 Add file: papers/{paper['category']}/{paper['filename']}")
        print()

    total = len(registry['papers'])
    ingested = sum(1 for p in registry['papers'] if p.get('ingested', False))
    print(f"{'='*70}")
    print(f"Status: {ingested}/{total} papers ingested")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Ingest finance papers into FinCanon')
    parser.add_argument('--force', action='store_true',
                        help='Re-ingest papers even if already ingested')
    parser.add_argument('--list', action='store_true',
                        help='List all papers and their ingestion status')

    args = parser.parse_args()

    if args.list:
        list_papers()
    else:
        ingest_all_papers(force=args.force)
