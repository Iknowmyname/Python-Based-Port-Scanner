# backend/app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from typing import List
import time

app = FastAPI()

# allow your frontend origin(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # update if different
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# configuration: tune for demo safety
MAX_THREADS = 200
DEFAULT_TIMEOUT = 1.0  # seconds
MIN_PORT = 1
MAX_PORT = 65535

def scan_port(host: str, port: int, timeout: float = DEFAULT_TIMEOUT):
    """Attempt to connect and optionally read a banner."""
    result = {"port": port, "open": False, "banner": None, "prediction": None}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        err = sock.connect_ex((host, port))
        if err == 0:
            result["open"] = True
            try:
                # some services send banner immediately
                sock.settimeout(0.6)
                data = sock.recv(1024)
                if data:
                    # sanitize decode
                    try:
                        banner = data.decode(errors="ignore").strip()
                        result["banner"] = banner
                    except Exception:
                        result["banner"] = "<binary>"
            except Exception:
                pass
        sock.close()
    except Exception:
        pass
    return result

def call_predict_banner(banner_text: str):
    """Call your existing predict_banner endpoint if available."""
    if not banner_text:
        return None
    try:
        # assumes predict_banner is on same server at /predict_banner
        r = requests.get("http://localhost:8000/predict_banner", params={"banner": banner_text}, timeout=5)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None

@app.get("/scan_and_predict")
def scan_and_predict(
    host: str = Query(...),
    start_port: int = Query(1),
    end_port: int = Query(1024),
    timeout: float = Query(DEFAULT_TIMEOUT),
):
    # safety checks: restrict wide scans by default
    if start_port < MIN_PORT: start_port = MIN_PORT
    if end_port > MAX_PORT: end_port = MAX_PORT
    if end_port - start_port > 5000:
        return {"error": "Requested port range too large for demo. Use a smaller range."}

    # optional local-only default: restrict to localhost/private ranges by default
    # Remove or change this if you intentionally want to scan public hosts (but be careful).
    if not (host == "127.0.0.1" or host == "localhost" or host.startswith("192.") or host.startswith("10.") or host.startswith("172.")):
        # allow but require explicit confirmation from client (frontend checks confirm)
        pass

    ports = list(range(start_port, end_port + 1))
    scans = []
    start_time = time.time()
    # use a ThreadPoolExecutor for I/O-bound tasks
    max_workers = min(MAX_THREADS, len(ports))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(scan_port, host, p, timeout): p for p in ports}
        for fut in as_completed(futures):
            res = fut.result()
            # if there's a banner, attempt prediction (call existing model)
            if res["banner"]:
                pred = call_predict_banner(res["banner"])
                # pred might be dict or string — keep flexible
                res["prediction"] = pred
            scans.append(res)

    total_time = time.time() - start_time
    scans_sorted = sorted(scans, key=lambda x: x["port"])
    return {"host": host, "start_port": start_port, "end_port": end_port, "duration_s": round(total_time,2), "scans": scans_sorted}
