import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [host, setHost] = useState("127.0.0.1"); // default local host
  const [startPort, setStartPort] = useState(1);
  const [endPort, setEndPort] = useState(1024);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  async function scanAndPredict() {
    setError(null);
    setResults(null);
    // safety: require localhost or private range by default
    if (!/^127\.0\.0\.1$/.test(host) && !/^localhost$/.test(host) && !host.startsWith("192.") && !host.startsWith("10.") && !host.startsWith("172.")) {
      if (!confirm("You are about to scan a non-local host. Do you have permission?")) return;
    }
    setRunning(true);
    try {
      const r = await axios.get("http://localhost:8000/scan_and_predict", {
        params: {
          host,
          start_port: Number(startPort),
          end_port: Number(endPort),
        },
        timeout: 120000, // allow for slow scans
      });
      setResults(r.data);
    } catch (e) {
      console.error(e);
      setError(e?.response?.data || e.message || String(e));
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">NetSense — Scan & Predict</h1>
          <div className="text-sm text-slate-500">Auto-scan banners → service predictions</div>
        </header>

        <section className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <label className="flex flex-col">
              <span className="text-sm font-medium text-slate-600">Target host</span>
              <input
                className="mt-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={host}
                onChange={(e) => setHost(e.target.value)}
                placeholder="127.0.0.1 or 192.168.1.10"
              />
            </label>

            <label className="flex flex-col">
              <span className="text-sm font-medium text-slate-600">Start port</span>
              <input
                type="number"
                className="mt-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={startPort}
                onChange={(e) => setStartPort(e.target.value)}
                min={1}
                max={65535}
              />
            </label>

            <label className="flex flex-col">
              <span className="text-sm font-medium text-slate-600">End port</span>
              <input
                type="number"
                className="mt-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={endPort}
                onChange={(e) => setEndPort(e.target.value)}
                min={1}
                max={65535}
              />
            </label>
          </div>

          <div className="mt-4 flex items-center gap-3">
            <button
              onClick={scanAndPredict}
              disabled={running}
              className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-60"
            >
              {running ? (
                <>
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Scanning...
                </>
              ) : (
                "Scan & Predict"
              )}
            </button>

            <button
              onClick={() => { setHost("127.0.0.1"); setStartPort(1); setEndPort(1024); setResults(null); setError(null); }}
              className="px-3 py-2 border rounded-md text-sm"
            >
              Reset
            </button>

            <div className="ml-auto text-sm text-slate-500">
              Default scans are limited to local/private IPs for demo safety.
            </div>
          </div>
        </section>

        <section>
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-100 text-red-800 rounded">
              <b>Error:</b> <span className="block mt-1 whitespace-pre-wrap">{JSON.stringify(error)}</span>
            </div>
          )}

          {!results && !error && (
            <div className="text-sm text-slate-500">No results yet. Click <b>Scan & Predict</b> to run a quick scan and see predictions for any discovered banners.</div>
          )}

          {results && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {results.scans?.map((r, idx) => (
                  <div key={idx} className="bg-white p-4 rounded-lg shadow">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-sm text-slate-500">Host</div>
                        <div className="text-lg font-medium">{results.host}:{r.port}</div>
                      </div>
                      <div className="text-sm text-slate-400">{r.open ? "OPEN" : "CLOSED"}</div>
                    </div>

                    <div className="mt-3">
                      <div className="text-xs text-slate-500">Banner</div>
                      <pre className="mt-1 text-sm bg-slate-100 p-2 rounded overflow-auto max-h-28">{r.banner || "<none>"}</pre>
                    </div>

                    <div className="mt-3">
                      <div className="text-xs text-slate-500">Prediction</div>
                      <div className="mt-1">
                        {r.prediction ? (
                          <div className="flex items-center justify-between">
                            <div className="text-sm font-semibold">{r.prediction}</div>
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => { navigator.clipboard.writeText(r.prediction); }}
                                className="text-xs px-2 py-1 border rounded"
                              >
                                Copy
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="text-sm text-slate-400">No prediction</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-4 text-sm text-slate-500">
                Summary: {results.scans.length} ports scanned — {results.scans.filter(s=>s.open).length} open.
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
