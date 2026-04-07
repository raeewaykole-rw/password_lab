import itertools
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional


def _chunked(iterable, size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def brute_force_attack(
    target_password: str,
    min_length: int = 1,
    max_length: int = 5,
    charset: str = string.ascii_lowercase + string.digits,
    workers: int = 8,
    chunk_size: int = 2000,
) -> Dict[str, object]:
    """
    Multi-threaded brute-force simulator.
    Returns metadata for analytics/logging.
    """
    start = time.perf_counter()
    attempts = 0
    found: Optional[str] = None

    if min_length < 1 or max_length < 1:
        raise ValueError("min_length and max_length must be >= 1")
    if min_length > max_length:
        raise ValueError("min_length cannot be greater than max_length")
    if not charset:
        raise ValueError("charset cannot be empty")
    if workers < 1:
        raise ValueError("workers must be >= 1")
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")

    def check_batch(batch):
        for guess in batch:
            if guess == target_password:
                return guess
        return None

    for length in range(min_length, max_length + 1):
        guesses = ("".join(c) for c in itertools.product(charset, repeat=length))
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            futures = []
            max_inflight = max(1, workers) * 4

            for batch in _chunked(guesses, max(1, chunk_size)):
                attempts += len(batch)
                futures.append(pool.submit(check_batch, batch))

                if len(futures) >= max_inflight:
                    for fut in as_completed(futures):
                        match = fut.result()
                        if match:
                            found = match
                            for pending in futures:
                                pending.cancel()
                            break
                    futures = []
                    if found:
                        break

            if not found:
                for fut in as_completed(futures):
                    match = fut.result()
                    if match:
                        found = match
                        for pending in futures:
                            pending.cancel()
                        break

            if found:
                break
        if found:
            break

    elapsed = time.perf_counter() - start
    return {
        "attack": "brute_force",
        "status": "cracked" if found else "failed",
        "password": found,
        "attempts": attempts,
        "time_taken_sec": round(elapsed, 4),
        "config": {
            "min_length": min_length,
            "max_length": max_length,
            "charset_size": len(charset),
            "workers": workers,
        },
    }
