import math
import re
from typing import Dict, List


COMMON_PATTERNS = [
    r"(.)\1{2,}",  # repeated chars
    r"(?:1234|12345|123456|qwerty|admin|password)",
]


def _estimate_crack_time_seconds(entropy_bits: float, guesses_per_second: int = 1_000_000):
    # Expected guesses ~= 2^(entropy-1)
    expected_guesses = 2 ** max(entropy_bits - 1, 0)
    return expected_guesses / guesses_per_second


def evaluate_password_strength(password: str) -> Dict[str, object]:
    charset = 0
    findings: List[str] = []

    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(c in "!@#$%^&*()_+-={}[]|:;'<>,.?/~`" for c in password):
        charset += 32

    entropy = len(password) * math.log2(charset) if charset else 0.0

    for pattern in COMMON_PATTERNS:
        if re.search(pattern, password.lower()):
            findings.append(f"Weak pattern detected: /{pattern}/")

    if len(password) < 8:
        findings.append("Too short: less than 8 characters")

    if entropy < 28:
        rating = "weak"
    elif entropy < 45:
        rating = "medium"
    else:
        rating = "strong"

    crack_time = _estimate_crack_time_seconds(entropy)

    return {
        "password_length": len(password),
        "charset_size": charset,
        "entropy_bits": round(entropy, 2),
        "estimated_crack_time_sec": round(crack_time, 2),
        "rating": rating,
        "findings": findings,
    }
