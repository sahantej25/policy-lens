"""Stage 1: fetch raw source pages/PDFs listed in data/sources.csv."""
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import RAW_DIR, RAW_MANIFEST, SOURCES_CSV, REQUEST_TIMEOUT, USER_AGENT


def _ext_for(url: str, content_type: str) -> str:
    if url.lower().endswith(".pdf") or "pdf" in content_type.lower():
        return "pdf"
    return "html"


def fetch_one(row: dict) -> dict:
    result = {**row, "status": "failed", "raw_path": None, "http_status": None, "notes": ""}
    try:
        resp = requests.get(
            row["url"], headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
        )
        result["http_status"] = resp.status_code
        if resp.status_code != 200:
            result["notes"] = f"non-200 response: {resp.status_code}"
            return result
        ext = _ext_for(row["url"], resp.headers.get("Content-Type", ""))
        raw_path = RAW_DIR / f"{row['source_id']}.{ext}"
        raw_path.write_bytes(resp.content)
        result["raw_path"] = str(raw_path)
        result["status"] = "ok"
    except requests.RequestException as exc:
        result["notes"] = f"request error: {exc}"
    return result


def run() -> list[dict]:
    if not SOURCES_CSV.exists():
        raise FileNotFoundError(f"Missing source list: {SOURCES_CSV}")
    with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [fetch_one(row) for row in rows]
    RAW_MANIFEST.write_text(json.dumps(results, indent=2), encoding="utf-8")

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"Ingested {ok}/{len(results)} sources. Manifest: {RAW_MANIFEST}")
    return results


if __name__ == "__main__":
    run()
