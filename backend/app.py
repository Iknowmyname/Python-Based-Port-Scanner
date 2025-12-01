# backend/app.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import subprocess
import joblib
import json
import shlex
from typing import Optional

app = FastAPI(title='NetSense API')

MODEL_PATH = 'ml/model_baseline.pkl'
model = None
try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None

class ScanRequest(BaseModel):
    host: str
    start_port: int = 1
    end_port: int = 1024

@app.post('/scan')
def scan(req: ScanRequest, background_tasks: BackgroundTasks):
    cmd = f"python scanner/scanner.py --host {shlex.quote(req.host)} --start-port {req.start_port} --end-port {req.end_port} --output scan_results.jsonl"
    background_tasks.add_task(subprocess.call, cmd, shell=True)
    return {"status": "started", "host": req.host}

@app.get('/predict_banner')
def predict_banner(banner: str):
    if not model:
        return {"error": "model not available"}
    probs = model.predict_proba([banner]).tolist()
    labels = model.classes_.tolist()
    pred = model.predict([banner]).tolist()
    return {"prediction": pred[0], "labels": labels, "probs": probs[0]}
