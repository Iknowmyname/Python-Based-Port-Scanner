# ml/auto_label.py
import json, re, sys
from collections import Counter

KEYMAP = [
    (r"SSH-2\\.0|OpenSSH", "ssh"),
    (r"nginx", "http:nginx"),
    (r"apache", "http:apache"),
    (r"HTTP/1\\.[01]|Server:", "http"),
    (r"Microsoft-IIS", "http:iis"),
    (r"FTP", "ftp"),
    (r"220 .*SMTP|ESMTP|Postfix|MAIL Service", "smtp"),
    (r"POP3", "pop3"),
    (r"IMAP", "imap"),
    (r"MariaDB|MySQL", "mysql"),
    (r"Redis", "redis"),
    (r"Elasticsearch", "elasticsearch"),
    (r"MongoDB", "mongodb"),
    (r"SMB|samba", "smb"),
    (r"mssql|Microsoft SQL", "mssql"),
    (r"VMware", "vmware"),
    (r"RDP|Remote Desktop", "rdp"),
    (r"Telnet", "telnet"),
    (r"VNC", "vnc"),
    (r"MSRPC|MS-RPC|RPC", "msrpc"),
    (r"NetBIOS", "netbios")
]

def label_banner(banner):
    if not banner:
        return "unknown"
    b = banner.lower()
    for pat, label in KEYMAP:
        if re.search(pat.lower(), b):
            return label
    return "unknown"

def run(infile="scan_results.jsonl", outfile="ml/labeled_banners.jsonl", max_examples=5000):
    cnt = Counter()
    written = 0
    with open(infile, "r", encoding="utf-8", errors="replace") as fi, open(outfile, "a", encoding="utf-8") as fo:
        for line in fi:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            banner = rec.get("banner") or ""
            label = label_banner(banner)
            out = {"banner": banner, "label": label, "port": rec.get("port")}
            fo.write(json.dumps(out) + "\n")
            cnt[label] += 1
            written += 1
            if written >= max_examples:
                break
    print("Wrote", written, "examples. Counts:", dict(cnt))

if __name__ == "__main__":
    infile = sys.argv[1] if len(sys.argv)>1 else "scan_results.jsonl"
    outfile = sys.argv[2] if len(sys.argv)>2 else "ml/labeled_banners.jsonl"
    run(infile, outfile)
