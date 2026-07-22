"""Stage 3: clean text, normalize metadata, dedupe near-identical records."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import CLEANED_JSONL, EXTRACTED_DIR, MIN_CLEAN_CHARS, SOURCES_CSV

BOILERPLATE_PATTERNS = [
    r"^\s*skip to (main )?content\s*$",
    r"^\s*(share|print|email) this page\s*$",
    r"^\s*last updated:?.*$",
    r"^\s*©.*$",
    r"^\s*all rights reserved\.?\s*$",
]
BOILERPLATE_RE = re.compile("|".join(BOILERPLATE_PATTERNS), re.IGNORECASE)


def clean_text(raw: str) -> str:
    lines = [ln.strip() for ln in raw.splitlines()]
    lines = [ln for ln in lines if ln and not BOILERPLATE_RE.match(ln)]
    text = "\n".join(lines)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def content_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def run() -> list[dict]:
    with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
        sources = {row["source_id"]: row for row in csv.DictReader(f)}

    records, seen_hashes = [], set()
    for source_id, meta in sources.items():
        extracted_path = EXTRACTED_DIR / f"{source_id}.json"
        if not extracted_path.exists():
            records.append(_missing_record(meta, "not extracted (ingest/extract failed)"))
            continue

        payload = json.loads(extracted_path.read_text(encoding="utf-8"))
        cleaned = clean_text(payload["text"])
        h = content_hash(cleaned)

        record = {
            "source_id": source_id,
            "source_title": meta["source_title"],
            "source_url": meta["url"],
            "issuing_body": meta["issuing_body"],
            "document_type": meta["document_type"],
            "topic_category": meta["topic_category"],
            "date_or_version": meta.get("date_or_version") or "not_provided",
            "source_format": meta["format"],
            "cleaned_text": cleaned,
            "char_count": len(cleaned),
            "content_hash": h,
            "extraction_notes": payload.get("extraction_notes", ""),
            "is_duplicate": False,
            "low_confidence": len(cleaned) < MIN_CLEAN_CHARS,
        }
        if h in seen_hashes:
            record["is_duplicate"] = True
            record["extraction_notes"] += " | duplicate content of an earlier source, excluded from chunking"
        else:
            seen_hashes.add(h)
        records.append(record)

    CLEANED_JSONL.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records), encoding="utf-8"
    )
    usable = sum(1 for r in records if not r.get("is_duplicate") and not r.get("missing"))
    print(f"Cleaned {len(records)} records, {usable} usable (non-duplicate, extracted). -> {CLEANED_JSONL}")
    return records


def _missing_record(meta: dict, note: str) -> dict:
    return {
        "source_id": meta["source_id"],
        "source_title": meta["source_title"],
        "source_url": meta["url"],
        "issuing_body": meta["issuing_body"],
        "document_type": meta["document_type"],
        "topic_category": meta["topic_category"],
        "date_or_version": meta.get("date_or_version") or "not_provided",
        "source_format": meta["format"],
        "cleaned_text": "",
        "char_count": 0,
        "content_hash": "",
        "extraction_notes": note,
        "is_duplicate": False,
        "low_confidence": True,
        "missing": True,
    }


if __name__ == "__main__":
    run()
