"use client";

import { useEffect, useRef, useState } from "react";

const WS_URL = process.env.NEXT_PUBLIC_BACKEND_WS || "ws://localhost:8000/ws";

export default function HomePage() {
  const [brief, setBrief] = useState("");
  const [logs, setLogs] = useState<Array<{id: string, message: string, timestamp: Date}>>([]);
  const [report, setReport] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const appendLog = (msg: string) => {
    const newLog = {
      id: Date.now().toString(),
      message: msg,
      timestamp: new Date()
    };
    setLogs((l) => [...l, newLog]);
  };

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const run = () => {
    if (isRunning) return;
    
    setLogs([]);
    setReport(null);
    setIsRunning(true);
    
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    
    ws.onopen = () => {
      setIsConnected(true);
      appendLog("Connected to server");
      if (brief.trim()) {
        ws.send(JSON.stringify({ brief }));
      } else {
        ws.send("");
      }
    };
    
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.event === "log") {
          appendLog(`${data.data}`);
        }
        if (data.event === "report") {
          setReport(data.data);
          appendLog("Report generated successfully!");
          setIsRunning(false);
        }
      } catch (e) {
        appendLog(`❌ Error parsing message: ${ev.data}`);
      }
    };
    
    ws.onerror = () => {
      appendLog("WebSocket connection error");
      setIsConnected(false);
      setIsRunning(false);
    };
    
    ws.onclose = () => {
      appendLog("Task completed");
      setIsConnected(false);
      setIsRunning(false);
      // Close the WebSocket connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  };

  const clearLogs = () => {
    setLogs([]);
    setReport(null);
  };

  return (
    <div style={{ 
      minHeight: "100vh", 
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: "20px",
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      display: "flex",
      alignItems: "center",
      justifyContent: "center"
    }}>
      <div style={{
        width: "min(96vw, 1280px)",
        margin: "0 auto",
        background: "white",
        borderRadius: "20px",
        boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
        overflow: "hidden"
      }}>
        {/* Header */}
        <div style={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          padding: "clamp(24px, 5vw, 48px)",
          textAlign: "center"
        }}>
          <h1 style={{
            fontSize: "clamp(1.6rem, 4.2vw, 2.6rem)",
            fontWeight: "700",
            margin: "0 0 10px 0",
            textShadow: "0 2px 4px rgba(0,0,0,0.3)"
          }}>
            Autonomous AI Task Agent
          </h1>
          <p style={{
            fontSize: "clamp(0.9rem, 2.2vw, 1.1rem)",
            margin: "0",
            opacity: "0.9"
          }}>
            Enter your research brief and watch the AI work its magic
          </p>
        </div>

        {/* Main Content */}
        <div style={{ padding: "clamp(24px, 4.5vw, 48px)" }}>
          {/* Input Section */}
          <div style={{ marginBottom: "30px" }}>
            <label style={{
              display: "block",
              fontSize: "1.1rem",
              fontWeight: "600",
              marginBottom: "15px",
              color: "#374151"
            }}>
              Research Brief
            </label>
            <textarea
              value={brief}
              onChange={(e) => setBrief(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                  e.preventDefault();
                  if (!isRunning && brief.trim()) {
                    run();
                  }
                }
              }}
              placeholder="e.g., 'Research the latest developments in quantum computing and provide a comprehensive summary with citations'"
              rows={4}
              style={{
                width: "100%",
                padding: "clamp(14px, 2.5vw, 20px)",
                border: "2px solid #e5e7eb",
                borderRadius: "12px",
                fontSize: "clamp(0.95rem, 2.4vw, 1rem)",
                fontFamily: "inherit",
                resize: "vertical",
                transition: "border-color 0.3s ease",
                outline: "none",
                boxSizing: "border-box"
              }}
              onFocus={(e) => e.target.style.borderColor = "#667eea"}
              onBlur={(e) => e.target.style.borderColor = "#e5e7eb"}
            />
            
            <div style={{ 
              display: "flex", 
              gap: "15px", 
              marginTop: "20px",
              alignItems: "center"
            }}>
              <button 
                onClick={run} 
                disabled={isRunning}
                style={{
                  background: isRunning ? "#9ca3af" : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "white",
                  border: "none",
                  padding: "15px 30px",
                  borderRadius: "10px",
                  fontSize: "1rem",
                  fontWeight: "600",
                  cursor: isRunning ? "not-allowed" : "pointer",
                  transition: "all 0.3s ease",
                  boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)"
                }}
                onMouseOver={(e) => {
                  if (!isRunning) {
                    e.currentTarget.style.transform = "translateY(-2px)";
                    e.currentTarget.style.boxShadow = "0 6px 20px rgba(102, 126, 234, 0.6)";
                  }
                }}
                onMouseOut={(e) => {
                  if (!isRunning) {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = "0 4px 15px rgba(102, 126, 234, 0.4)";
                  }
                }}
              >
                {isRunning ? "Processing..." : "Run Research"}
              </button>
              
              <button 
                onClick={clearLogs}
                style={{
                  background: "#f3f4f6",
                  color: "#374151",
                  border: "2px solid #e5e7eb",
                  padding: "13px 25px",
                  borderRadius: "10px",
                  fontSize: "1rem",
                  fontWeight: "500",
                  cursor: "pointer",
                  transition: "all 0.3s ease"
                }}
              >
                Clear
              </button>
              
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginLeft: "auto"
              }}>
                <div style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  background: isConnected ? "#10b981" : "#ef4444"
                }}></div>
                <span style={{ fontSize: "0.9rem", color: "#6b7280" }}>
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
            </div>
          </div>

          {/* Logs Section */}
          {logs.length > 0 && (
            <div style={{ marginBottom: "30px" }}>
              <h2 style={{
                fontSize: "1.3rem",
                fontWeight: "600",
                marginBottom: "20px",
                color: "#374151",
                display: "flex",
                alignItems: "center",
                gap: "10px"
              }}>
                Live Progress
              </h2>
              <div style={{
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                borderRadius: "12px",
                padding: "clamp(14px, 3vw, 20px)",
                maxHeight: "32vh",
                overflowY: "auto",
                fontFamily: "Monaco, 'Courier New', monospace"
              }}>
                {logs.map((log) => (
                  <div key={log.id} style={{
                    padding: "8px 0",
                    borderBottom: "1px solid #e2e8f0",
                    fontSize: "0.9rem",
                    color: "#374151"
                  }}>
                    <span style={{ color: "#6b7280", fontSize: "0.8rem" }}>
                      {log.timestamp.toLocaleTimeString()}
                    </span>
                    <span style={{ marginLeft: "10px" }}>
                      {log.message}
                    </span>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            </div>
          )}

          {/* Report Section */}
          {report && (
            <div>
              <h2 style={{
                fontSize: "1.3rem",
                fontWeight: "600",
                marginBottom: "20px",
                color: "#374151",
                display: "flex",
                alignItems: "center",
                gap: "10px"
              }}>
                Research Report
              </h2>
              
              <div style={{
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                borderRadius: "12px",
                padding: "25px",
                marginBottom: "20px"
              }}>
                <h3 style={{
                  fontSize: "1.1rem",
                  fontWeight: "600",
                  marginBottom: "15px",
                  color: "#1f2937"
                }}>
                  Summary
                </h3>
                <pre style={{
                  whiteSpace: "pre-wrap",
                  lineHeight: "1.75",
                  color: "#374151",
                  fontSize: "1rem",
                  fontFamily: "inherit",
                  margin: 0
                }}>
                  {report.summary || "No summary available"}
                </pre>
              </div>

              {report.citations && report.citations.length > 0 && (
                <div>
                  <h3 style={{
                    fontSize: "1.1rem",
                    fontWeight: "600",
                    marginBottom: "15px",
                    color: "#1f2937",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px"
                  }}>
                    Sources & Citations
                  </h3>
                  <div style={{
                    display: "grid",
                    gap: "12px"
                  }}>
                    {report.citations.map((citation: any, i: number) => (
                      <div key={i} style={{
                        background: "white",
                        border: "1px solid #e5e7eb",
                        borderRadius: "8px",
                        padding: "15px",
                        transition: "all 0.3s ease"
                      }}>
                        <a 
                          href={citation.url} 
                          target="_blank" 
                          rel="noreferrer"
                          style={{
                            color: "#667eea",
                            textDecoration: "none",
                            fontWeight: "500",
                            fontSize: "1rem",
                            display: "block"
                          }}
                          onMouseOver={(e) => {
                            e.currentTarget.style.color = "#764ba2";
                            e.currentTarget.parentElement!.style.borderColor = "#667eea";
                            e.currentTarget.parentElement!.style.transform = "translateY(-2px)";
                          }}
                          onMouseOut={(e) => {
                            e.currentTarget.style.color = "#667eea";
                            e.currentTarget.parentElement!.style.borderColor = "#e5e7eb";
                            e.currentTarget.parentElement!.style.transform = "translateY(0)";
                          }}
                        >
                          {citation.title || citation.url}
                        </a>
                        <div style={{
                          fontSize: "0.8rem",
                          color: "#6b7280",
                          marginTop: "5px"
                        }}>
                          {citation.url}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
