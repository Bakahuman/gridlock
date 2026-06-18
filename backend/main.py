import os
import io
import csv
import uuid

import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from forecaster import Forecaster
from recommender import recommend
import feedback

DETECTION_URL = os.environ.get("DETECTION_URL", "http://localhost:8001")
DATA = os.path.join(os.path.dirname(__file__), "..", "data")

app = FastAPI(title="Gridlock Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

forecaster = None


@app.on_event("startup")
def load():
    global forecaster
    try:
        forecaster = Forecaster()
    except Exception as e:
        # allow the API to boot before models are trained
        print("forecaster not loaded yet:", e)


@app.get("/health")
def health():
    return {"ok": True, "forecaster_loaded": forecaster is not None}


# core endpoint: image in -> detect -> forecast -> recommend
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            r = await client.post(
                f"{DETECTION_URL}/detect",
                files={"file": (file.filename, content, file.content_type)},
            )
            r.raise_for_status()
        except Exception as e:
            raise HTTPException(502, f"detection service error: {e}")

    events = r.json().get("events", [])
    results = []

    for ev in events:
        item = {"event": ev, "forecast": None, "recommendation": None}
        if ev["violation_type"] == "lane_block" and forecaster is not None:
            ctx = {
                "corridor": ev.get("corridor"),
                "zone": ev.get("zone"),
                "event_cause": "vehicle_breakdown",
                "event_type": "unplanned",
            }
            fc = forecaster.forecast(ev["event_id"], ctx)
            item["forecast"] = fc
            item["recommendation"] = recommend(fc)
        results.append(item)

    return {"results": results}


# forecast directly from a context payload (no image), used by the
# scenario panel in the UI
@app.post("/forecast")
def forecast_only(ctx: dict):
    if forecaster is None:
        raise HTTPException(503, "forecaster not loaded")
    eid = ctx.get("event_id", str(uuid.uuid4()))
    fc = forecaster.forecast(eid, ctx)
    rec = recommend(fc)
    return {"forecast": fc, "recommendation": rec}


@app.post("/feedback")
def add_feedback(record: dict):
    return feedback.log_outcome(record)


@app.get("/feedback/summary")
def feedback_summary():
    return feedback.summary()


# parking hotspots for the map, sampled from the PS1 police data
@app.get("/hotspots")
def hotspots(limit: int = 2000):
    path = os.path.join(DATA, "police_violations.csv")
    points = []
    if not os.path.exists(path):
        return {"points": []}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["latitude"])
                lng = float(row["longitude"])
            except (ValueError, KeyError):
                continue
            if 12.7 <= lat <= 13.3 and 77.3 <= lng <= 77.9:
                points.append({"lat": lat, "lng": lng})
            if len(points) >= limit:
                break
    return {"points": points}
