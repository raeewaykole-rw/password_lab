import time
from pathlib import Path
from typing import Dict, Optional


def dictionary_attack(target_password: str, wordlist_path: str) -> Dict[str, object]:
    start = time.perf_counter()
    attempts = 0
    found: Optional[str] = None

    path = Path(wordlist_path)
    if not path.exists():
        raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            attempts += 1
            candidate = line.strip()
            if candidate == target_password:
                found = candidate
                break

    elapsed = time.perf_counter() - start
    return {
        "attack": "dictionary",
        "status": "cracked" if found else "failed",
        "password": found,
        "attempts": attempts,
        "time_taken_sec": round(elapsed, 4),
        "config": {"wordlist": str(path)},
    }
