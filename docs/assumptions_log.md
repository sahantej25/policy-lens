# Assumptions Log

1. **No confidential/internal data**: only publicly accessible government pages are used this cycle, per project brief.
2. **Robots/ToS compliance**: `ingest.py` sends a descriptive User-Agent and respects standard HTTP responses; it does not bypass authentication, rate limits, or robots directives. Any site requiring special access is out of scope and should be flagged via the project email channel, not scraped around.
3. **HTML structure varies by agency**: extraction targets `<main>`/`<article>`/`<body>` and strips nav/script/footer — a general heuristic, not a site-specific parser. Manual spot-checks of `data/extracted/*.json` are recommended before treating a source as fully clean.
4. **PDF text layer assumed present**: `extract.py` does not run OCR. Scanned/image-only PDFs will yield empty text and are flagged in `extraction_notes` — that's expected, not a bug.
5. **Dedup is content-hash based**: near-duplicate pages with materially different wording (e.g., updated policy text) are *not* deduped — only exact-normalized-text matches are. This avoids accidentally discarding a revised version.
6. **Local embeddings only for this cycle**: `all-MiniLM-L6-v2` is used for zero API cost and full offline reproducibility, per the brief's "fully workable with local embedding models" requirement. Swapping in OpenAI embeddings for comparison is possible but not wired in by default.
7. **Chunk size (220 words / 40 overlap)** is a starting default tuned for policy-procedure prose (roughly paragraph-to-section length); it is a config value, not a hardcoded constant, so it can be tuned per corpus.
8. **`date_or_version`** is left as `not_provided` when a source page doesn't expose a visible revision date — federal pages frequently don't. This is recorded explicitly rather than guessed.
9. **This pipeline stops at retrieval.** No summarization, answer generation, or policy interpretation is performed — retrieval output is raw passages + source references only, per the brief's exclusion of a "decision engine" or "compliance interpretation system."
