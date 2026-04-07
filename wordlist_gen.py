from pathlib import Path
from typing import Iterable, List


def generate_wordlist(name: str, dob: str, extras: Iterable[str] = ()) -> List[str]:
    base = name.strip()
    compact_dob = dob.replace("-", "").strip()
    words = {
        base,
        f"{base}123",
        f"{base}@123",
        f"{base}{compact_dob}",
        f"{base.capitalize()}@{compact_dob[-4:]}" if compact_dob else f"{base.capitalize()}@123",
    }
    for item in extras:
        item = item.strip()
        if item:
            words.add(item)

    return sorted(words)


def save_wordlist(words: List[str], output_path: str = "wordlists/custom.txt") -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for word in words:
            f.write(f"{word}\n")
    return str(path)
