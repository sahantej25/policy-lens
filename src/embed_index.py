"""Stage 5: embed chunks locally and build a FAISS cosine-similarity index."""
import json
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import CHUNK_STORE_PATH, CHUNKS_JSONL, EMBEDDING_MODEL, FAISS_INDEX_PATH


def load_chunks() -> list[dict]:
    return [json.loads(line) for line in CHUNKS_JSONL.read_text(encoding="utf-8").splitlines() if line]


def run() -> None:
    chunks = load_chunks()
    if not chunks:
        raise ValueError("No chunks found. Run chunk.py first.")

    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)  # cosine similarity via inner product

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype(np.float32))
    faiss.write_index(index, str(FAISS_INDEX_PATH))

    CHUNK_STORE_PATH.write_text(json.dumps(chunks, ensure_ascii=False, indent=None), encoding="utf-8")
    print(f"Indexed {len(chunks)} chunks, dim={embeddings.shape[1]} -> {FAISS_INDEX_PATH}")


if __name__ == "__main__":
    run()
