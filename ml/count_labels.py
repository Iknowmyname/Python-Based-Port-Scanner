# ml/count_labels.py
import json, collections
from pathlib import Path

p = Path("ml/labeled_banners.jsonl")
if not p.exists():
    print("ml/labeled_banners.jsonl not found.")
    raise SystemExit(1)

cnt = collections.Counter()
lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
for ln in lines:
    try:
        r = json.loads(ln)
    except Exception:
        continue
    cnt[r.get("label", "unknown")] += 1

print("TOTAL LINES:", len(lines))
print()
for label, c in cnt.most_common():
    print(f"{label:20} {c}")
