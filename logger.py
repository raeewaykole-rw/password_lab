import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict


_lock = Lock()


def log_event(data: Dict[str, object], log_path: str = "reports/log.jsonl") -> None:
    payload = dict(data)
    payload["time"] = datetime.now(timezone.utc).isoformat()

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with _lock:
        with path.open("a", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=True)
            f.write("\n")
