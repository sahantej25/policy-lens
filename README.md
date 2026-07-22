# PolicyLens

Local, low-cost ingestion and indexing pipeline for public policy and procedure documents. Produces a clean, chunked, embedded, source-traceable corpus that a future retrieval-grounded policy assistant can query. This project does **not** interpret policy, make eligibility determinations, or answer questions on its own — it prepares and retrieves source material for human review.

## What it does

`sources.csv` (curated public URLs) → **ingest** raw HTML/PDF → **extract** text → **clean** & dedupe → **metadata** manifest → **chunk** → **embed + index** (FAISS, local sentence-transformers) → **retrieve** top-k passages with source references.

## Project structure

```
policy-lens/
├── config.py                  # paths & pipeline parameters
├── pipeline.py                 # CLI entry point
├── requirements.txt
├── src/
│   ├── ingest.py               # stage 1: download raw sources
│   ├── extract.py              # stage 2: HTML/PDF -> text
│   ├── clean.py                # stage 3: clean, normalize, dedupe
│   ├── metadata.py             # stage: build reviewer-facing manifest
│   ├── chunk.py                # stage 4: passage chunking
│   ├── embed_index.py          # stage 5: embeddings + FAISS index
│   └── retrieve.py             # stage 6: query the index
├── data/
│   ├── sources.csv             # INPUT: curated source inventory (edit this)
│   ├── raw/                    # downloaded HTML/PDF + raw_manifest.json
│   ├── extracted/              # per-source extracted text JSON
│   ├── cleaned/corpus.jsonl    # cleaned, deduped corpus with metadata
│   ├── metadata_manifest.csv   # one row per source, for review
│   ├── chunks/chunks.jsonl     # chunk-level records
│   └── index/                  # FAISS index + chunk store
├── notebooks/walkthrough.ipynb # run pipeline + sample retrieval queries
└── docs/                       # source selection, assumptions, limitations
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python pipeline.py all                     # run every stage
python pipeline.py ingest                  # or run stages individually:
python pipeline.py extract
python pipeline.py clean
python pipeline.py metadata
python pipeline.py chunk
python pipeline.py embed
python pipeline.py query "Where is the escalation or appeal process described?"
```

Or open `notebooks/walkthrough.ipynb` for an annotated run with sample queries and inspectable output tables.

## Extending the corpus

Add rows to `data/sources.csv` (columns: `source_id, url, source_title, issuing_body, document_type, topic_category, format, date_or_version, notes`), then rerun `python pipeline.py all`. All stages are idempotent per source_id and safe to rerun.

To reuse this pipeline with internal/restricted documents instead of public URLs: drop files into `data/raw/` named `{source_id}.{html|pdf}`, add matching rows to `sources.csv`, and skip the `ingest` stage.

## Design choices

- **Chunking**: sliding word window (220 words, 40-word overlap) — balances context completeness against retrieval precision; tune in `config.py`.
- **Embeddings**: local `sentence-transformers/all-MiniLM-L6-v2` — no API cost, no data leaves the machine. Swap `EMBEDDING_MODEL` in `config.py` for a stronger model if needed.
- **Index**: FAISS `IndexFlatIP` over L2-normalized vectors (= cosine similarity). Exact search, fine at this corpus size (tens–hundreds of docs).
- **Confidence flags**: `low_confidence` is set on corpus records with thin extracted text, and on query results with weak similarity scores — both are review signals, not hidden.

See `docs/` for source selection rationale, assumptions, and limitations.
