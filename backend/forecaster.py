import os
import json
from datetime import datetime

from catboost import CatBoostClassifier, CatBoostRegressor

MODELS = os.path.join(os.path.dirname(__file__), "..", "models")


def clean(v):
    if v is None or v in ("NULL", ""):
        return "unknown"
    return v


class Forecaster:
    def __init__(self):
        with open(os.path.join(MODELS, "report.json")) as f:
            self.report = json.load(f)
        self.features = self.report["features"]
        self.severity_features = self.report["severity_features"]

        self.severity = CatBoostClassifier()
        self.severity.load_model(os.path.join(MODELS, "severity.cbm"))
        self.closure = CatBoostClassifier()
        self.closure.load_model(os.path.join(MODELS, "closure.cbm"))
        self.clearance = CatBoostRegressor()
        self.clearance.load_model(os.path.join(MODELS, "clearance.cbm"))

        # spread for the clearance band, from the trainer's reported MAE
        self.clearance_mae = self.report["clearance"].get("mae_minutes", 90.0)

    def _row(self, ctx, feature_list):
        ts = ctx.get("timestamp") or datetime.utcnow()
        base = {
            "event_type": clean(ctx.get("event_type", "unplanned")),
            "event_cause": clean(ctx.get("event_cause", "vehicle_breakdown")),
            "veh_type": clean(ctx.get("veh_type")),
            "corridor": clean(ctx.get("corridor")),
            "zone": clean(ctx.get("zone")),
            "hour": ts.hour,
            "dow": ts.weekday(),
            "month": ts.month,
        }
        return [base[k] for k in feature_list]

    # ctx carries the location/context for a detected lane_block event
    def forecast(self, event_id, ctx):
        sev_row = self._row(ctx, self.severity_features)
        full_row = self._row(ctx, self.features)

        sev_proba = float(self.severity.predict_proba([sev_row])[0][1])
        severity = "High" if sev_proba >= 0.5 else "Low"
        sev_conf = sev_proba if severity == "High" else 1 - sev_proba

        closure_p = float(self.closure.predict_proba([full_row])[0][1])

        mins = float(self.clearance.predict([full_row])[0])
        mins = max(1.0, mins)
        low = max(1.0, mins - self.clearance_mae)
        high = mins + self.clearance_mae

        return {
            "event_id": event_id,
            "severity": severity,
            "severity_confidence": round(sev_conf, 3),
            "closure_probability": round(closure_p, 3),
            "expected_clearance_minutes": round(mins, 1),
            "clearance_low": round(low, 1),
            "clearance_high": round(high, 1),
        }
