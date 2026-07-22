from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW_DIR = DATA / "raw"
EXTRACTED_DIR = DATA / "extracted"
CLEANED_DIR = DATA / "cleaned"
CHUNKS_DIR = DATA / "chunks"
INDEX_DIR = DATA / "index"

SOURCES_CSV = DATA / "sources.csv"
RAW_MANIFEST = RAW_DIR / "raw_manifest.json"
METADATA_CSV = DATA / "metadata_manifest.csv"
CLEANED_JSONL = CLEANED_DIR / "corpus.jsonl"
CHUNKS_JSONL = CHUNKS_DIR / "chunks.jsonl"
FAISS_INDEX_PATH = INDEX_DIR / "policy.index"
CHUNK_STORE_PATH = INDEX_DIR / "chunk_store.json"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE_WORDS = 220
CHUNK_OVERLAP_WORDS = 40
MIN_CLEAN_CHARS = 300  # below this, record is flagged low_confidence
REQUEST_TIMEOUT = 20
USER_AGENT = "PolicyLensBot/1.0 (public-policy-research; contact=project-team)"

for _d in (RAW_DIR, EXTRACTED_DIR, CLEANED_DIR, CHUNKS_DIR, INDEX_DIR):
    _d.mkdir(parents=True, exist_ok=True)
