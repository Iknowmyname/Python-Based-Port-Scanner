# ml/cve_index.py
import argparse, pandas as pd, numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import joblib

def build_index(cve_csv="ml/cve_index.csv", embed_model="all-MiniLM-L6-v2", out="ml/cve_index.pkl"):
    df = pd.read_csv(cve_csv, names=["cve","summary"]) if os.path.exists(cve_csv) else pd.DataFrame([])
    s = SentenceTransformer(embed_model)
    emb = s.encode(df['summary'].fillna("").tolist(), show_progress_bar=True)
    nn = NearestNeighbors(n_neighbors=5, metric='cosine').fit(emb)
    joblib.dump({"df":df, "emb":emb, "nn":nn, "model_name":embed_model}, out)
    print("Saved index to", out)

def query_index(index_pkl, text, topk=5):
    obj = joblib.load(index_pkl)
    s = SentenceTransformer(obj['model_name'])
    q = s.encode([text])
    dists, idx = obj['nn'].kneighbors(q, n_neighbors=topk)
    df = obj['df']
    results = []
    for i, d in zip(idx[0], dists[0]):
        results.append({"cve": df.iloc[i]['cve'], "summary": df.iloc[i]['summary'], "dist": float(d)})
    return results

if __name__ == "__main__":
    import sys, os
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build_index()
    else:
        text = " ".join(sys.argv[1:])
        print(query_index('ml/cve_index.pkl', text))
