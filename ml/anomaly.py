# ml/anomaly.py
import argparse, joblib
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest

def load_banners(path):
    df = pd.read_csv(path)
    return df['banner'].fillna("").astype(str).tolist(), df

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="ml/train_data.csv")
    p.add_argument("--out", default="ml/anomaly_scores.csv")
    p.add_argument("--model", default="all-MiniLM-L6-v2")
    args = p.parse_args()

    banners, df = load_banners(args.data)
    print("Encoding", len(banners), "banners with", args.model)
    sbert = SentenceTransformer(args.model)
    emb = sbert.encode(banners, show_progress_bar=True, convert_to_numpy=True)
    print("Embeddings shape:", emb.shape)
    iso = IsolationForest(contamination=0.02, random_state=42)
    preds = iso.fit_predict(emb)
    scores = iso.decision_function(emb)
    df['anomaly'] = (preds == -1)
    df['anomaly_score'] = -scores
    df.to_csv(args.out, index=False)
    print("Wrote anomalies to", args.out)
    print(df.sort_values('anomaly_score', ascending=False).head(10)[['banner','label','anomaly','anomaly_score']])
