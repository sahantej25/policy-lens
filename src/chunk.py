"""Stage 4: split cleaned documents into overlapping passage-level chunks."""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import CHUNK_OVERLAP_WORDS, CHUNK_SIZE_WORDS, CHUNKS_JSONL, CLEANED_JSONL

CARRY_FIELDS = [
    "source_title", "source_url", "issuing_body", "document_type",
    "topic_category", "date_or_version", "source_format",
]


def chunk_words(words: list[str], size: int, overlap: int):
    step = max(size - overlap, 1)
    for start in range(0, len(words), step):
        piece = words[start : start + size]
        if piece:
            yield piece
        if start + size >= len(words):
            break


def run() -> list[dict]:
    docs = [json.loads(line) for line in CLEANED_JSONL.read_text(encoding="utf-8").splitlines() if line]
    chunks = []
    for doc in docs:
        if doc.get("missing") or doc.get("is_duplicate") or not doc["cleaned_text"].strip():
            continue
        words = doc["cleaned_text"].split()
        for i, piece in enumerate(chunk_words(words, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS)):
            chunk = {
                "chunk_id": f"{doc['source_id']}_c{i:03d}",
                "source_id": doc["source_id"],
                "chunk_index": i,
                "text": " ".join(piece),
                "word_count": len(piece),
                **{k: doc[k] for k in CARRY_FIELDS},
            }
            chunks.append(chunk)

    CHUNKS_JSONL.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks), encoding="utf-8")
    print(f"Created {len(chunks)} chunks from {len(docs)} documents -> {CHUNKS_JSONL}")
    return chunks


if __name__ == "__main__":
    run()
