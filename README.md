# Gridlock

CV-based traffic intelligence for the Gridlock Hackathon 2.0 (PS3).

A traffic camera frame is analysed for lane-blocking vehicles and helmet
violations. Lane-block events are pushed into a forecaster trained on real
Bengaluru incident data, which predicts severity, closure likelihood and
clearance time, then recommends a deployment plan. Outcomes feed back to
sharpen the models.

## Repo layout

```
shared/             contract both halves import (violation-event schema)
detection_service/  vision half  (runs on the 3060 GPU)
backend/            forecast + recommend + feedback (runs on CPU)
frontend/           React + Tailwind + shadcn dashboard
data/               Astram (PS2) and police (PS1) datasets
models/             trained model files land here
```

## Who builds what

- Dev A: backend forecasting, feedback loop, frontend.
- Dev B: detection_service (LocateAnything on the 3060).

Both build against `shared/schema.py`. The two services talk over HTTP, so
they can be developed and run independently.

## Run order

```
# 1. backend (CPU)
cd backend
pip install -r requirements.txt
python train_models.py        # trains the 3 forecast models into ../models
uvicorn main:app --reload --port 8000

# 2. detection service (3060 box)
cd detection_service
pip install -r requirements.txt
uvicorn service:app --reload --port 8001

# 3. frontend
cd frontend
npm install
npm run dev
```

Set `DETECTION_URL` in the backend env to point at the detection service
(defaults to http://localhost:8001).
