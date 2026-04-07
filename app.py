import json
import os
from collections import Counter
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__)


def load_logs(path: str = "reports/log.jsonl"):
    log_path = Path(path)
    if not log_path.exists():
        return []
    logs = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return logs


@app.route("/")
def dashboard():
    logs = load_logs()
    latest = list(reversed(logs[-50:]))
    status_counts = Counter(log.get("status", "unknown") for log in logs)
    attack_counts = Counter(log.get("attack", "unknown") for log in logs)
    cracked = status_counts.get("cracked", 0)
    failed = status_counts.get("failed", 0)
    return render_template(
        "dashboard.html",
        logs=latest,
        total=len(logs),
        cracked=cracked,
        failed=failed,
        status_counts=dict(status_counts),
        attack_counts=dict(attack_counts),
    )


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes"}
    app.run(debug=debug_mode, host="127.0.0.1", port=5000)
