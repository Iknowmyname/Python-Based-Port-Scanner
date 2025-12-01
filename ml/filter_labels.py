# ml/filter_labels.py
import json
from pathlib import Path

p = Path("ml/labeled_banners.jsonl")
out = Path("ml/labeled_banners_filtered.jsonl")

if not p.exists():
    print("ml/labeled_banners.jsonl not found.")
    raise SystemExit(1)

lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
keep = []
for ln in lines:
    try:
        r = json.loads(ln)
    except Exception:
        continue
    lbl = r.get("label")
    if lbl and lbl != "unknown":
        keep.append(ln)

out.write_text("\n".join(keep), encoding="utf-8")
print(f"Wrote {len(keep)} filtered examples to {out}")
