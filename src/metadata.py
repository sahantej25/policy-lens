"""Stage: build a flat, reviewer-friendly metadata manifest from the cleaned corpus."""
import csv
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import CLEANED_JSONL, METADATA_CSV

FIELDS = [
    "source_id", "source_title", "source_url", "issuing_body", "document_type",
    "topic_category", "date_or_version", "source_format", "char_count",
    "is_duplicate", "low_confidence", "missing", "extraction_notes",
]


def run() -> None:
    rows = [json.loads(line) for line in CLEANED_JSONL.read_text(encoding="utf-8").splitlines() if line]
    with open(METADATA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            r.setdefault("missing", False)
            writer.writerow(r)
    print(f"Metadata manifest: {METADATA_CSV} ({len(rows)} rows)")


if __name__ == "__main__":
    run()
