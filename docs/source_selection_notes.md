# Source Selection Notes

## Scope
Corpus is bounded to **public-facing U.S. federal service/benefit eligibility and procedure pages** — a coherent topic area covering retirement, disability, unemployment, health coverage, immigration adjustment-of-status, and veterans benefits. This mirrors the kind of policy/procedure lookup an advisory team performs daily, while staying entirely on official public domains.

## Why these sources
- All entries in `data/sources.csv` are official government domains (`.gov`): SSA, IRS, DOL, USCIS, HealthCare.gov, VA.gov, USA.gov, Benefits.gov.
- Each page is either an **eligibility guidance**, **service instruction**, or **appeal/escalation process** page — matching the sample query set in the assignment brief.
- Government domains were prioritized over secondary/aggregator sites for authority and lower risk of stale or inaccurate paraphrasing.
- ~15 seed sources are included as a starting inventory; the brief's 40–80 target is reached by extending `sources.csv` with additional pages from the same domains (e.g., more SSA benefit types, more USCIS form categories, state-level equivalents). The pipeline requires no code changes to scale — only more rows.

## How to extend
1. Identify additional official pages within the same topic families.
2. Add a row per source to `data/sources.csv` with a unique `source_id`.
3. Rerun `python pipeline.py all`.

## Excluded by design
- Any page requiring login or paywall.
- Third-party summaries, forums, or SEO content sites.
- PDFs/pages that return non-200 responses are logged in `data/raw/raw_manifest.json` with the failure reason, not silently dropped.
