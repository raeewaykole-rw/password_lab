import time
from pathlib import Path
from typing import Dict, Optional


def hybrid_attack(
    target_password: str, wordlist_path: str, max_suffix: int = 9999
) -> Dict[str, object]:
    """
    Hybrid attack: dictionary word + numeric suffix.
    """
    start = time.perf_counter()
    attempts = 0
    found: Optional[str] = None

    path = Path(wordlist_path)
    if not path.exists():
        raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        words = [w.strip() for w in f if w.strip()]

    for word in words:
        attempts += 1
        if word == target_password:
            found = word
            break

        for num in range(max_suffix + 1):
            attempts += 1
            candidate = f"{word}{num}"
            if candidate == target_password:
                found = candidate
                break
        if found:
            break

    elapsed = time.perf_counter() - start
    return {
        "attack": "hybrid",
        "status": "cracked" if found else "failed",
        "password": found,
        "attempts": attempts,
        "time_taken_sec": round(elapsed, 4),
        "config": {"wordlist": str(path), "max_suffix": max_suffix},
    }
