"""Stage 6: retrieval smoke testing — query the index, return top-k passages with sources."""
import json
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import CHUNK_STORE_PATH, EMBEDDING_MODEL, FAISS_INDEX_PATH

_model = None
_index = None
_chunks = None


def _load():
    global _model, _index, _chunks
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
        _index = faiss.read_index(str(FAISS_INDEX_PATH))
        _chunks = json.loads(CHUNK_STORE_PATH.read_text(encoding="utf-8"))


def search(query: str, top_k: int = 5, min_score: float = 0.2) -> list[dict]:
    """Return top-k chunks for a query. Low-scoring hits are flagged low_confidence
    rather than silently returned as if they were a confident match."""
    _load()
    vec = _model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(vec)
    scores, idxs = _index.search(vec.astype(np.float32), top_k)

    results = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx == -1:
            continue
        chunk = _chunks[idx]
        results.append(
            {
                "score": round(float(score), 4),
                "low_confidence": float(score) < min_score,
                "source_title": chunk["source_title"],
                "source_url": chunk["source_url"],
                "issuing_body": chunk["issuing_body"],
                "topic_category": chunk["topic_category"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
            }
        )
    return results


def print_results(query: str, results: list[dict]) -> None:
    print(f"\nQuery: {query}")
    if not results:
        print("  No results — index may be empty.")
        return
    for r in results:
        flag = " [LOW CONFIDENCE]" if r["low_confidence"] else ""
        print(f"  [{r['score']}]{flag} {r['source_title']} ({r['issuing_body']})")
        print(f"    {r['source_url']}")
        print(f"    {r['text'][:220]}...")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is the appeal or escalation process?"
    print_results(q, search(q))
