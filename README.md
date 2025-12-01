# NetSense — AI-Powered Network Recon & Risk Prioritization (Demo)

This repository is a runnable demo that converts simple port banners into service labels (ML), provides an anomaly detection experiment, and includes a minimal FastAPI backend and React frontend scaffold.

**Warning:** Only scan hosts/networks you own or have explicit permission to scan.

## Repo structure
```
netsense_project/
├─ README.md
├─ docker-compose.yml
├─ .gitignore
├─ scanner/
│  ├─ scanner.py
│  └─ requirements.txt
├─ ml/
│  ├─ labeled_banners.jsonl
│  ├─ labeled_banners_filtered.jsonl
│  ├─ preprocess.py
│  ├─ auto_label.py
│  ├─ train.py
│  ├─ train_model.py
│  ├─ anomaly.py
│  ├─ cve_index.py
│  ├─ requirements.txt
│  └─ show_labeled.py
├─ backend/
│  ├─ app.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ package.json
│  └─ src/App.jsx
└─ demo/
   └─ README.md
```

## Quick start (local, host-based scanner)

1. (Optional) Start demo HTTP servers:
   - If you have Docker: `docker-compose up -d` (starts nginx on 8080/8081)
   - Or run simple Python HTTP servers: `python -m http.server 8080` and `python -m http.server 8081`

2. Run scanner to collect banners:
   ```bash
   python scanner/scanner.py --host 127.0.0.1 --start-port 8080 --end-port 8081 --output scan_results.jsonl --workers 20
   ```

3. Auto-label & filter dataset:
   ```bash
   python ml/auto_label.py scan_results.jsonl ml/labeled_banners.jsonl
   python ml/filter_labels.py
   ```

4. Prepare training data and train model:
   ```bash
   python ml/preprocess.py --in ml/labeled_banners_filtered.jsonl --out ml/train_data.csv
   pip install -r ml/requirements.txt   # or pip install scikit-learn pandas joblib
   python ml/train_model.py --data ml/train_data.csv --out ml/model_baseline.pkl
   ```

5. Run backend for inference:
   ```bash
   pip install -r backend/requirements.txt
   uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   curl "http://localhost:8000/predict_banner?banner=HTTP/1.1%20200%20OK%20Server:%20nginx/1.22.0"
   ```

## Deploy to GitHub
1. Initialize repo and commit:
   ```bash
   git init
   git add .
   git commit -m "Initial NetSense demo scaffold"
   gh repo create netsense-demo --public --source=. --push
   ```
2. Or create a new repo on GitHub and push the folder.

## Notes
- This is a demo scaffold. Improve dataset and models for production use.
- Always get permission before scanning other people's networks.
