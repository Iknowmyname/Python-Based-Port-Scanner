# scanner/scanner.py
import socket
import argparse
import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_TIMEOUT = 1.0
HTTP_PORTS = {80, 8080, 8000, 81, 8081}

def probe_port(host: str, port: int, timeout=DEFAULT_TIMEOUT):
    record = {
        "host": host,
        "port": port,
        "open": False,
        "banner": None,
        "ts": datetime.datetime.utcnow().isoformat()
    }
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        if result == 0:
            record['open'] = True
            try:
                # If we suspect HTTP-like service, send a simple GET to provoke a response.
                if port in HTTP_PORTS:
                    req = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                    try:
                        sock.sendall(req.encode())
                    except Exception:
                        pass
                    sock.settimeout(1.0)
                    data = b""
                    try:
                        data = sock.recv(4096)
                    except Exception:
                        pass
                else:
                    sock.settimeout(0.5)
                    try:
                        data = sock.recv(2048)
                    except Exception:
                        data = b""
                if data:
                    record['banner'] = data.decode(errors='ignore').strip()
            except Exception:
                pass
        sock.close()
    except Exception:
        pass
    return record

def run_scan(host: str, start_port: int, end_port: int, output: str, workers=100):
    ports = list(range(start_port, end_port + 1))
    start = datetime.datetime.utcnow()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(probe_port, host, p): p for p in ports}
        with open(output, 'a', encoding='utf-8') as f:
            for fut in as_completed(futures):
                rec = fut.result()
                if rec:
                    f.write(json.dumps(rec) + "\n")
    end = datetime.datetime.utcnow()
    print(f"Scan complete. Start: {start.isoformat()} End: {end.isoformat()}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    parser.add_argument('--start-port', type=int, default=1)
    parser.add_argument('--end-port', type=int, default=1024)
    parser.add_argument('--output', default='scan_results.jsonl')
    parser.add_argument('--workers', type=int, default=100)
    args = parser.parse_args()
    run_scan(args.host, args.start_port, args.end_port, args.output, args.workers)
