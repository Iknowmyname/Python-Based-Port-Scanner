# ml/show_labeled.py  (fixed)
import json
from pathlib import Path
from collections import Counter

p = Path("ml/labeled_banners.jsonl")
if not p.exists():
    print("ml/labeled_banners.jsonl not found.")
    raise SystemExit(1)

lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
cnt = Counter()
print("TOTAL LINES:", len(lines))
print()
for i, ln in enumerate(lines[:20], start=1):
    try:
        r = json.loads(ln)
    except Exception as e:
        print(f"{i:02d}: parse error: {e}")
        continue
    label = r.get("label", "??")
    banner = r.get("banner") or ""
    banner_snippet = banner[:200].replace("\r", "\\r").replace("\n", "\\n")
    cnt[label] += 1
    print(f"{i:02d}: label={label} banner={banner_snippet}")
print()
print("COUNTS (sample of labels):")
for k, v in cnt.most_common():
    print(f"  {k:20} {v}")
