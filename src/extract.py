"""Stage 2: extract raw text from downloaded HTML/PDF files."""
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import EXTRACTED_DIR, RAW_MANIFEST

DROP_TAGS = ["script", "style", "nav", "footer", "header", "noscript", "form", "svg"]


def extract_html(raw_path: Path) -> tuple[str, str]:
    soup = BeautifulSoup(raw_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for tag in soup(DROP_TAGS):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text(separator="\n")
    return text, "extracted via BeautifulSoup, main/article/body scope, boilerplate tags dropped"


def extract_pdf(raw_path: Path) -> tuple[str, str]:
    import pdfplumber

    pages = []
    with pdfplumber.open(raw_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    text = "\n".join(pages)
    note = f"extracted via pdfplumber, {len(pages)} pages"
    if not text.strip():
        note += "; no extractable text (possibly scanned/image PDF, OCR not run)"
    return text, note


def run() -> list[dict]:
    if not RAW_MANIFEST.exists():
        raise FileNotFoundError("Run ingest.py first to produce raw_manifest.json")
    manifest = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))

    results = []
    for row in manifest:
        record = {"source_id": row["source_id"], "status": "skipped", "notes": row.get("notes", "")}
        if row["status"] != "ok" or not row.get("raw_path"):
            record["notes"] = record["notes"] or "no raw file (ingest failed)"
            results.append(record)
            continue

        raw_path = Path(row["raw_path"])
        try:
            if raw_path.suffix == ".pdf":
                text, note = extract_pdf(raw_path)
            else:
                text, note = extract_html(raw_path)
            out_path = EXTRACTED_DIR / f"{row['source_id']}.json"
            out_path.write_text(
                json.dumps({"source_id": row["source_id"], "text": text, "extraction_notes": note}, indent=2),
                encoding="utf-8",
            )
            record.update(status="ok", notes=note, extracted_path=str(out_path))
        except Exception as exc:  # noqa: BLE001 - log and continue, don't kill the batch
            record.update(status="failed", notes=f"extraction error: {exc}")
        results.append(record)

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"Extracted {ok}/{len(results)} sources.")
    return results


if __name__ == "__main__":
    run()
