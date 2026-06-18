import csv
import json
import os
from datetime import datetime

from catboost import CatBoostClassifier, CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, mean_absolute_error

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "astram_events.csv")
OUT = os.path.join(os.path.dirname(__file__), "..", "models")

# corridor almost perfectly encodes priority in this data (label leakage),
# so it is excluded from the severity model but kept for closure/clearance
# where it acts as legitimate geography.
CAT_FEATURES = ["event_type", "event_cause", "veh_type", "corridor", "zone"]
SEVERITY_CAT = ["event_type", "event_cause", "veh_type", "zone"]
NUM_FEATURES = ["hour", "dow", "month"]
FEATURES = CAT_FEATURES + NUM_FEATURES
SEVERITY_FEATURES = SEVERITY_CAT + NUM_FEATURES


def parse_dt(s):
    if not s or s in ("NULL", ""):
        return None
    s = s.split("+")[0].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def clean(v):
    if v is None or v in ("NULL", ""):
        return "unknown"
    return v


def load_rows():
    with open(DATA, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_features(r):
    start = parse_dt(r["start_datetime"])
    return {
        "event_type": clean(r["event_type"]),
        "event_cause": clean(r["event_cause"]),
        "veh_type": clean(r["veh_type"]),
        "corridor": clean(r["corridor"]),
        "zone": clean(r["zone"]),
        "hour": start.hour if start else -1,
        "dow": start.weekday() if start else -1,
        "month": start.month if start else -1,
    }


def to_matrix(samples, feature_list=FEATURES):
    return [[s[k] for k in feature_list] for s in samples]


def train_severity(rows):
    X, y = [], []
    for r in rows:
        if r["priority"] in ("High", "Low"):
            X.append(build_features(r))
            y.append(1 if r["priority"] == "High" else 0)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    cat_idx = [SEVERITY_FEATURES.index(c) for c in SEVERITY_CAT]
    m = CatBoostClassifier(iterations=300, depth=6, learning_rate=0.1, verbose=False)
    m.fit(to_matrix(Xtr, SEVERITY_FEATURES), ytr, cat_features=cat_idx)
    pred = m.predict(to_matrix(Xte, SEVERITY_FEATURES))
    proba = m.predict_proba(to_matrix(Xte, SEVERITY_FEATURES))[:, 1]
    m.save_model(os.path.join(OUT, "severity.cbm"))
    return {"accuracy": accuracy_score(yte, pred), "auc": roc_auc_score(yte, proba), "n": len(X)}


def train_closure(rows):
    X, y = [], []
    for r in rows:
        v = r["requires_road_closure"]
        if v in ("TRUE", "FALSE"):
            X.append(build_features(r))
            y.append(1 if v == "TRUE" else 0)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    cat_idx = [FEATURES.index(c) for c in CAT_FEATURES]
    m = CatBoostClassifier(iterations=300, depth=6, learning_rate=0.1, verbose=False,
                           auto_class_weights="Balanced")
    m.fit(to_matrix(Xtr), ytr, cat_features=cat_idx)
    proba = m.predict_proba(to_matrix(Xte))[:, 1]
    m.save_model(os.path.join(OUT, "closure.cbm"))
    return {"auc": roc_auc_score(yte, proba), "n": len(X)}


def train_clearance(rows):
    X, y = [], []
    for r in rows:
        a = parse_dt(r["start_datetime"])
        b = parse_dt(r["closed_datetime"])
        if a and b and b > a:
            mins = (b - a).total_seconds() / 60.0
            # drop absurd outliers so the model is usable
            if 1 <= mins <= 1440:
                X.append(build_features(r))
                y.append(mins)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    cat_idx = [FEATURES.index(c) for c in CAT_FEATURES]
    m = CatBoostRegressor(iterations=400, depth=6, learning_rate=0.1, verbose=False,
                          loss_function="MAE")
    m.fit(to_matrix(Xtr), ytr, cat_features=cat_idx)
    pred = m.predict(to_matrix(Xte))
    m.save_model(os.path.join(OUT, "clearance.cbm"))
    return {"mae_minutes": mean_absolute_error(yte, pred), "n": len(X)}


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = load_rows()
    report = {
        "severity": train_severity(rows),
        "closure": train_closure(rows),
        "clearance": train_clearance(rows),
        "features": FEATURES,
        "severity_features": SEVERITY_FEATURES,
        "cat_features": CAT_FEATURES,
        "severity_cat": SEVERITY_CAT,
    }
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
