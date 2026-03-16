"use client";

import { useState } from "react";

export default function Home() {
  const [ingestStatus, setIngestStatus] = useState<string>("Waiting for command...");
  const [chatMessage, setChatMessage] = useState<string>("");
  const [chatResponse, setChatResponse] = useState<string>("No messages yet.");

  // Function to hit our /api/ingest route
  const handleIngest = async (framework: string) => {
    setIngestStatus(`Triggering pipeline for ${framework}...`);
    try {
      const res = await fetch("http://localhost:8000/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ framework_name: framework }),
      });
      const data = await res.json();
      setIngestStatus(`✅ Success: ${data.message}`);
    } catch (error) {
      setIngestStatus("❌ Error: Could not connect to backend.");
    }
  };

  // Function to hit our /api/chat/stream route
  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    setChatResponse("Waiting for AI response...");
    try {
      const res = await fetch("http://localhost:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: chatMessage, framework_name: "react" }),
      });
      const data = await res.json();
      setChatResponse(`🤖 AI Says: ${data.message}`);
      setChatMessage(""); // Clear input
    } catch (error) {
      setChatResponse("❌ Error: Could not connect to backend.");
    }
  };

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-200 p-10 font-sans">
      <div className="max-w-4xl mx-auto space-y-12">
        
        {/* Header */}
        <header className="border-b border-neutral-800 pb-6">
          <h1 className="text-3xl font-bold text-white tracking-tight">DocThread <span className="text-blue-500">Workspace</span></h1>
          <p className="text-neutral-400 mt-2">Local-First Documentation & RAG Engine</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* PANEL 1: The Ingestion Engine */}
          <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-xl font-semibold text-white mb-4">1. Ingestion Engine</h2>
            <p className="text-sm text-neutral-400 mb-6">Trigger the backend ETL pipeline to scrape and vector-embed documentation.</p>
            
            <div className="flex space-x-4 mb-6">
              <button 
                onClick={() => handleIngest("pandas")}
                className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-sm font-medium transition-colors border border-neutral-700"
              >
                Download Pandas Docs
              </button>
              <button 
                onClick={() => handleIngest("react")}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
              >
                Download React Docs
              </button>
            </div>

            <div className="bg-black/50 rounded-lg p-4 border border-neutral-800 font-mono text-sm text-green-400">
              {ingestStatus}
            </div>
          </section>

          {/* PANEL 2: The Chat Interface */}
          <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-xl font-semibold text-white mb-4">2. AI Chat (Tracer Bullet)</h2>
            <p className="text-sm text-neutral-400 mb-6">Send a test message to the FastAPI backend placeholder.</p>
            
            <form onSubmit={handleChat} className="space-y-4">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Ask about React..."
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-white placeholder-neutral-600"
                required
              />
              <button 
                type="submit"
                className="w-full px-4 py-3 bg-white text-black hover:bg-neutral-200 rounded-lg text-sm font-bold transition-colors"
              >
                Send Message
              </button>
            </form>

            <div className="mt-6 bg-black/50 rounded-lg p-4 border border-neutral-800 font-mono text-sm text-blue-400 min-h-[80px]">
              {chatResponse}
            </div>
          </section>

        </div>
      </div>
    </main>
  );
}