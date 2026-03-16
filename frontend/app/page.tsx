"use client";

import { useState } from "react";

const API_BASE = "http://localhost:8000/api";

export default function ApiTesterPage() {
  const [framework, setFramework] = useState("pandas");
  const [query, setQuery] = useState("How do I create a DataFrame?");
  const [chatMessage, setChatMessage] = useState("What does useEffect do?");
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // --- Helper to call the backend and log the result ---
  const callApi = async (endpoint: string, payload: any) => {
    setLoading(true);
    const startTime = Date.now();
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      const timeTaken = Date.now() - startTime;
      
      // Add to our on-screen terminal
      setLogs((prev) => [
        { endpoint, status: response.status, time: `${timeTaken}ms`, data },
        ...prev,
      ]);
    } catch (error: any) {
      setLogs((prev) => [
        { endpoint, status: "ERROR", error: error.message },
        ...prev,
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 p-8 font-mono">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="border-b border-slate-800 pb-4">
          <h1 className="text-3xl font-bold text-white tracking-tight">🚀 DocThread Mission Control</h1>
          <p className="text-slate-500 mt-2">Testing all FastAPI endpoints from the Next.js Frontend</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* LEFT COLUMN: Controls */}
          <div className="space-y-6">
            
            {/* 1. INGESTION ENGINE */}
            <section className="bg-slate-900 p-6 rounded-xl border border-slate-800">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                ⚙️ 1. Ingestion Engine
              </h2>
              <div className="mb-4">
                <label className="block text-sm text-slate-400 mb-1">Target Framework</label>
                <input 
                  type="text" 
                  value={framework} 
                  onChange={(e) => setFramework(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex flex-wrap gap-3">
                <button 
                  onClick={() => callApi("/ingest/scrape", { framework_name: framework })}
                  className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm transition"
                  disabled={loading}
                >
                  Trigger Scrape Only
                </button>
                <button 
                  onClick={() => callApi("/ingest/vectorize", { framework_name: framework })}
                  className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded text-sm transition"
                  disabled={loading}
                >
                  Trigger Vectorize Only
                </button>
                <button 
                  onClick={() => callApi("/ingest/full", { framework_name: framework })}
                  className="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded text-sm transition font-bold"
                  disabled={loading}
                >
                  Run Full Pipeline
                </button>
              </div>
            </section>

            {/* 2. SYNTAX MAPPER (SEARCH) */}
            <section className="bg-slate-900 p-6 rounded-xl border border-slate-800">
              <h2 className="text-xl font-semibold text-white mb-4">🔍 2. Vector Search (Syntax Mapper)</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Search Query</label>
                  <input 
                    type="text" 
                    value={query} 
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <button 
                  onClick={() => callApi("/chat/search", { query: query, framework_name: framework, top_k: 3 })}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded text-sm transition"
                  disabled={loading}
                >
                  Search ChromaDB Database
                </button>
              </div>
            </section>

            {/* 3. AI CHAT STREAM */}
            <section className="bg-slate-900 p-6 rounded-xl border border-slate-800">
              <h2 className="text-xl font-semibold text-white mb-4">💬 3. AI Chat Endpoint</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Message</label>
                  <input 
                    type="text" 
                    value={chatMessage} 
                    onChange={(e) => setChatMessage(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
                <button 
                  onClick={() => callApi("/chat/stream", { message: chatMessage, framework_name: framework })}
                  className="w-full bg-amber-600 hover:bg-amber-500 text-white px-4 py-2 rounded text-sm transition"
                  disabled={loading}
                >
                  Test Chat Connection
                </button>
              </div>
            </section>

          </div>

          {/* RIGHT COLUMN: The Output Terminal */}
          <div className="bg-black p-6 rounded-xl border border-slate-800 flex flex-col h-[800px]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                🖥️ Response Terminal
              </h2>
              <button 
                onClick={() => setLogs([])}
                className="text-slate-500 hover:text-white text-sm underline"
              >
                Clear
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto bg-slate-950 p-4 rounded border border-slate-800 custom-scrollbar">
              {logs.length === 0 ? (
                <div className="text-slate-600 italic text-center mt-20">
                  Awaiting commands... Fire an API request to see the JSON output.
                </div>
              ) : (
                <div className="space-y-6">
                  {logs.map((log, index) => (
                    <div key={index} className="animate-fade-in-up">
                      <div className="flex gap-3 text-xs mb-2 items-center">
                        <span className={`px-2 py-1 rounded font-bold ${log.status === 200 ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'}`}>
                          {log.status}
                        </span>
                        <span className="text-blue-400 font-semibold">{log.endpoint}</span>
                        <span className="text-slate-500">{log.time}</span>
                      </div>
                      <pre className="bg-slate-900 p-3 rounded text-sm text-emerald-400 overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(log.data, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}