"""Single entry point to run pipeline stages.

Usage:
    python pipeline.py all
    python pipeline.py ingest|extract|clean|metadata|chunk|embed
    python pipeline.py query "your question here"
"""
import sys

from src import chunk, clean, embed_index, extract, ingest, metadata, retrieve

STAGES = {
    "ingest": ingest.run,
    "extract": extract.run,
    "clean": clean.run,
    "metadata": metadata.run,
    "chunk": chunk.run,
    "embed": embed_index.run,
}


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    if cmd == "all":
        for name, fn in STAGES.items():
            print(f"\n=== {name} ===")
            fn()
    elif cmd == "query":
        q = " ".join(sys.argv[2:]) or "What is the appeal or escalation process?"
        retrieve.print_results(q, retrieve.search(q))
    elif cmd in STAGES:
        STAGES[cmd]()
    else:
        print(f"Unknown stage: {cmd}\n")
        print(__doc__)


if __name__ == "__main__":
    main()
