import os
import json
from datetime import datetime

LOG = os.path.join(os.path.dirname(__file__), "feedback_log.jsonl")


# record an actual outcome against what was predicted for an event
def log_outcome(record):
    record["logged_at"] = datetime.utcnow().isoformat()
    with open(LOG, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def _read():
    if not os.path.exists(LOG):
        return []
    out = []
    with open(LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# summary the dashboard shows: how close predictions have been
def summary():
    rows = _read()
    if not rows:
        return {"count": 0}

    sev_correct = sum(
        1 for r in rows if r.get("predicted_severity") == r.get("actual_severity")
    )
    clear_err = [
        abs(r["predicted_clearance_minutes"] - r["actual_clearance_minutes"])
        for r in rows
        if r.get("predicted_clearance_minutes") is not None
        and r.get("actual_clearance_minutes") is not None
    ]
    mae = sum(clear_err) / len(clear_err) if clear_err else None

    return {
        "count": len(rows),
        "severity_accuracy": round(sev_correct / len(rows), 3),
        "clearance_mae_minutes": round(mae, 1) if mae is not None else None,
    }
