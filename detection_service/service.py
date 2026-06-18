import json

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from detector import get_detector
from rules import build_events

app = FastAPI(title="Gridlock Detection Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = get_detector()

PROMPTS = [
    "cars, trucks, buses parked at the roadside",
    "motorcycle riders",
    "helmets",
    "license plate",
]


@app.get("/health")
def health():
    return {"ok": True, "detector": type(detector).__name__}


# detect violations in one image.
# no_parking_zone and context are optional JSON strings from the caller.
@app.post("/detect")
async def detect(
    file: UploadFile = File(...),
    no_parking_zone: str = Form(None),
    context: str = Form(None),
):
    image_bytes = await file.read()
    detections = detector.detect(image_bytes, PROMPTS)

    zone = json.loads(no_parking_zone) if no_parking_zone else _default_zone()
    ctx = json.loads(context) if context else {"corridor": "Tumkur Road", "zone": "Peenya"}

    events = build_events(detections, no_parking_zone=zone, context=ctx)
    return {"events": events, "raw_detections": detections}


# a sensible default no-parking zone so the demo works without manual drawing
def _default_zone():
    return {"x1": 100, "y1": 180, "x2": 400, "y2": 420}
