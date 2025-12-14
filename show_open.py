# show_open.py
import json
from pathlib import Path

p = Path('scan_results.jsonl')
if not p.exists():
    print('scan_results.jsonl not found.')
    raise SystemExit(1)
for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get('open'):
        print(f"{r.get('host')}:{r.get('port')}  OPEN")
        b = r.get('banner')
        if b:
            print('BANNER:', b[:500].replace('\r','\\r').replace('\n','\\n'))
        else:
            print('BANNER: <none>')
        print('-'*60)
