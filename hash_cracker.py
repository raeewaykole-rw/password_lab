import hashlib
import time
from pathlib import Path
from typing import Dict, Optional


SUPPORTED = {"md5", "sha256"}


def _hash_word(word: str, algorithm: str) -> str:
    if algorithm == "md5":
        return hashlib.md5(word.encode("utf-8")).hexdigest()
    if algorithm == "sha256":
        return hashlib.sha256(word.encode("utf-8")).hexdigest()
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def crack_hash(hash_value: str, algorithm: str, wordlist_path: str) -> Dict[str, object]:
    if algorithm not in SUPPORTED:
        raise ValueError(f"Algorithm must be one of: {', '.join(sorted(SUPPORTED))}")

    start = time.perf_counter()
    attempts = 0
    found: Optional[str] = None

    path = Path(wordlist_path)
    if not path.exists():
        raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            attempts += 1
            word = line.strip()
            if _hash_word(word, algorithm) == hash_value.lower():
                found = word
                break

    elapsed = time.perf_counter() - start
    return {
        "attack": "hash_crack",
        "status": "cracked" if found else "failed",
        "password": found,
        "attempts": attempts,
        "time_taken_sec": round(elapsed, 4),
        "config": {"algorithm": algorithm, "wordlist": str(path)},
    }
