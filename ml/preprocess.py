# ml/preprocess.py
import json, re, argparse
from pathlib import Path
import pandas as pd

def clean_banner(s):
    if not s:
        return ""
    s = s.replace("\\r"," ").replace("\\n"," ").replace("\n"," ").replace("\r"," ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.lower()
    return s

def extract_version_tokens(s):
    if not s: return ""
    tokens = re.findall(r"(v?\d+(?:\.\d+){0,2}(?:[a-z0-9\-\.]*)?)", s, flags=re.I)
    return " ".join(tokens[:3])

def load_jsonl(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            r = json.loads(line)
        except:
            continue
        banner = r.get("banner") or ""
        rows.append({"banner_raw": banner, "banner": clean_banner(banner), "label": r.get("label","unknown"), "port": r.get("port")})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", default="ml/labeled_banners_filtered.jsonl")
    p.add_argument("--out", dest="outfile", default="ml/train_data.csv")
    args = p.parse_args()
    df = load_jsonl(args.infile)
    df = df[df['label'].notna() & (df['label'] != "unknown")]
    df['port'] = df['port'].fillna(-1).astype(int)
    df['vertokens'] = df['banner'].apply(extract_version_tokens)
    df.to_csv(args.outfile, index=False)
    print("Wrote", args.outfile, "with", len(df), "rows")
