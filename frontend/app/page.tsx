"use client";

import { useEffect, useRef, useState } from "react";

const WS_URL = process.env.NEXT_PUBLIC_BACKEND_WS || "ws://localhost:8000/ws";

export default function HomePage() {
  const [brief, setBrief] = useState("");
  const [logs, setLogs] = useState<string[]>([]);
  const [report, setReport] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const appendLog = (msg: string) => setLogs((l) => [...l, msg]);

  const run = () => {
    setLogs([]);
    setReport(null);
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => {
      const payload = brief.trim() ? { brief } : "";
      ws.send(JSON.stringify(payload || brief || ""));
    };
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.event === "log") appendLog(data.data);
        if (data.event === "report") setReport(data.data);
      } catch (e) {
        appendLog(String(ev.data));
      }
    };
    ws.onerror = () => appendLog("WebSocket error");
    ws.onclose = () => appendLog("Run finished");
  };

  return (
    <main style={{ padding: 20, maxWidth: 900, margin: "0 auto", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto" }}>
      <h1>Autonomous Multi-Tool AI Task Agent</h1>
      <p>Enter a brief and click Run to stream logs and see a final report with citations.</p>
      <textarea
        value={brief}
        onChange={(e) => setBrief(e.target.value)}
        placeholder="e.g., Summarize UAE telehealth companies with citations"
        rows={6}
        style={{ width: "100%", fontFamily: "inherit", padding: 10 }}
      />
      <div style={{ marginTop: 10 }}>
        <button onClick={run} style={{ padding: "8px 16px", cursor: "pointer" }}>Run</button>
      </div>

      <section style={{ marginTop: 20 }}>
        <h2>Logs</h2>
        <ul>
          {logs.map((l, i) => (
            <li key={i} style={{ whiteSpace: "pre-wrap" }}>{l}</li>
          ))}
        </ul>
      </section>

      {report && (
        <section style={{ marginTop: 20 }}>
          <h2>Report</h2>
          <pre style={{ background: "#f6f6f6", padding: 12, overflowX: "auto" }}>
            {JSON.stringify(report, null, 2)}
          </pre>
          <h3>Citations</h3>
          <ul>
            {(report.citations || []).map((c: any, i: number) => (
              <li key={i}>
                <a href={c.url} target="_blank" rel="noreferrer">{c.title || c.url}</a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
