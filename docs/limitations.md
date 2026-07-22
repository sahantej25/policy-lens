# Limitations

- **Not a policy interpretation system.** Retrieval output is source passages, not conclusions. Any first-pass note prepared from these results still needs analyst review before use.
- **Extraction is heuristic, not site-specific.** Pages with unusual layouts (heavy JS rendering, non-standard nav structure) may extract noisy or partial text. `low_confidence` flags catch short-text cases but not all noisy-but-long extractions — spot-check recommended.
- **No OCR.** Scanned/image PDFs will produce empty extracted text and are flagged, not silently skipped, but are not recoverable without adding an OCR step.
- **Dedup is exact-match only** (post-normalization). Two pages that say the same thing in different words will both be retained — by design (avoids false-deduping updated content), but means some redundancy can appear in results.
- **Corpus freshness**: this is a point-in-time snapshot. Re-running `ingest.py` periodically is required to keep pace with policy updates; the pipeline has no built-in change-detection/versioning yet.
- **Exact-search FAISS index** (`IndexFlatIP`) scales fine to hundreds of documents but would need an approximate index (e.g., HNSW/IVF) for much larger corpora.
- **Embedding model** (`all-MiniLM-L6-v2`) is a compact general-purpose model chosen for cost/speed; retrieval quality on domain-specific legal/policy phrasing may improve with a larger or domain-tuned model — noted as a future upgrade, not implemented here.
- **Not a public-facing tool.** This is an internal preparation-layer prototype only, per project scope.
