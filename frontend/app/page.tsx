"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { 
  Terminal, Search, MessageSquare, Settings, 
  BookOpen, ChevronRight, Loader2, Save 
} from "lucide-react";

export default function DocThreadDashboard() {
  // --- STATE ---
  const [activeFramework, setActiveFramework] = useState("pandas");
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  
  // Doc Viewer State
  const [docContent, setDocContent] = useState<string>("Welcome to DocThread. Select a framework and ask a question or use the search bar to pull raw documentation.");
  const [activeSources, setActiveSources] = useState<{source_file: string}[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  // Settings State
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    provider: "gemini",
    model: "gemini-2.5-flash",
    api_key: "",
    ollama_base_url: "http://localhost:11434"
  });

  const chatEndRef = useRef<HTMLDivElement>(null);

  // --- INITIAL LOAD ---
  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- API CALLS ---
  const fetchSettings = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/settings");
      const data = await res.json();
      setSettings(data);
    } catch (e) {
      console.error("Failed to load settings", e);
    }
  };

  const saveSettings = async () => {
    try {
      await fetch("http://localhost:8000/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      setShowSettings(false);
      alert("Settings Saved!");
    } catch (e) {
      console.error("Failed to save settings", e);
    }
  };

  const handleRawSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setDocContent("Searching ChromaDB...");
    try {
      const res = await fetch("http://localhost:8000/api/chat/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          framework_name: activeFramework,
          top_k: 3
        }),
      });
      const data = await res.json();
      
      let newDocView = `# Raw Search Results for: "${searchQuery}"\n\n`;
      data.results.forEach((result: any, index: number) => {
        newDocView += `### Source: ${result.metadata.source_file}\n`;
        newDocView += `\`\`\`text\n${result.content}\n\`\`\`\n\n---\n\n`;
      });
      
      setDocContent(newDocView);
    } catch (e) {
      setDocContent("Error fetching raw documentation.");
    }
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsTyping(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          framework_name: activeFramework,
          model: settings.model
        }),
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let done = false;
      let aiText = "";
      let foundSources = false;

      // Add a blank AI message to update
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          aiText += chunk;

          // Check if this chunk contains our secret __SOURCES__ tag
          if (!foundSources && aiText.includes("__SOURCES__")) {
            foundSources = true;
            // Extract the JSON array
            const parts = aiText.split("\n\n");
            const sourcesString = parts[0].replace("__SOURCES__", "");
            try {
              const parsedSources = JSON.parse(sourcesString);
              setActiveSources(parsedSources);
              // Update the Doc Viewer automatically!
              setDocContent(`# Active Context\nThe AI is currently reading from:\n\n${parsedSources.map((s:any) => `* **${s.source_file}**`).join('\n')}\n\n*Waiting for analysis...*`);
            } catch(e) { console.error("Source parse error", e); }
            
            // Remove the sources string from what we show the user
            aiText = aiText.substring(parts[0].length + 2);
          }

          // Update the chat UI
          setMessages((prev) => {
            const newMsgs = [...prev];
            newMsgs[newMsgs.length - 1].content = foundSources ? aiText.split("__SOURCES__")[1]?.substring(aiText.indexOf('\n\n') + 2) || aiText : aiText;
            return newMsgs;
          });
        }
      }
    } catch (error) {
      console.error("Stream failed", error);
      setMessages((prev) => [...prev, { role: "assistant", content: "⚠️ Connection to AI failed." }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0E1117] text-gray-200 font-sans overflow-hidden">
      
      {/* ================= LEFT SIDEBAR (Frameworks) ================= */}
      <div className="w-64 bg-[#161B22] border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800 flex items-center gap-2">
          <Terminal className="text-blue-500" size={24} />
          <h1 className="font-bold text-xl tracking-tight text-white">DocThread</h1>
        </div>
        
        <div className="p-4 flex-grow">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Libraries</h2>
          <div className="flex flex-col gap-1">
            {["pandas", "react", "numpy"].map((fw) => (
              <button
                key={fw}
                onClick={() => setActiveFramework(fw)}
                className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors text-sm ${
                  activeFramework === fw 
                  ? "bg-blue-600/20 text-blue-400 font-medium" 
                  : "hover:bg-gray-800 text-gray-400"
                }`}
              >
                <BookOpen size={16} />
                <span className="capitalize">{fw}</span>
              </button>
            ))}
          </div>
        </div>

        <button 
          onClick={() => setShowSettings(true)}
          className="p-4 border-t border-gray-800 flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
        >
          <Settings size={18} />
          <span>Engine Settings</span>
        </button>
      </div>

      {/* ================= CENTER PANEL (Doc Viewer) ================= */}
      <div className="flex-grow flex flex-col bg-[#0D1117] border-r border-gray-800 min-w-0">
        <div className="h-14 border-b border-gray-800 flex items-center px-4 bg-[#161B22]">
          <form onSubmit={handleRawSearch} className="flex-grow flex items-center max-w-2xl bg-[#0D1117] border border-gray-700 rounded-md overflow-hidden focus-within:border-blue-500 transition-colors">
            <div className="pl-3 text-gray-500"><Search size={16} /></div>
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={`Search raw ${activeFramework} documentation...`}
              className="w-full bg-transparent border-none focus:outline-none px-3 py-1.5 text-sm text-gray-200"
            />
          </form>
          <div className="ml-4 flex gap-2">
            <button className="flex items-center gap-1 bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded text-xs font-medium transition-colors">
              <Save size={14} /> Save Page
            </button>
          </div>
        </div>

        <div className="flex-grow overflow-y-auto p-8 prose prose-invert prose-blue max-w-none">
          {/* We use ReactMarkdown to render the fetched documentation nicely */}
          <ReactMarkdown>{docContent}</ReactMarkdown>
        </div>
      </div>

      {/* ================= RIGHT PANEL (AI Chat) ================= */}
      <div className="w-[450px] flex flex-col bg-[#161B22]">
        <div className="h-14 border-b border-gray-800 flex items-center px-4 justify-between bg-[#161B22]">
          <div className="flex items-center gap-2 font-medium text-white">
            <MessageSquare size={18} className="text-blue-500" />
            <span>DocThread AI</span>
          </div>
          <span className="text-xs px-2 py-1 rounded-full bg-blue-900/30 text-blue-400 border border-blue-800/50">
            {settings.provider}
          </span>
        </div>

        {/* Chat History */}
        <div className="flex-grow overflow-y-auto p-4 flex flex-col gap-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-10 text-sm">
              Ask a question about {activeFramework.toUpperCase()}. <br/>
              I will search the local ChromaDB and explain it.
            </div>
          )}
          
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-lg px-4 py-3 text-sm ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-800 border border-gray-700 text-gray-200 prose prose-invert prose-sm prose-p:leading-relaxed'
              }`}>
                {msg.role === 'assistant' ? (
                   <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex items-center gap-2 text-gray-500 text-sm p-2">
              <Loader2 size={16} className="animate-spin" /> Retrieving context...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t border-gray-800 bg-[#0D1117]">
          <form onSubmit={handleChatSubmit} className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="w-full bg-[#161B22] border border-gray-700 focus:border-blue-500 rounded-lg pl-4 pr-10 py-3 text-sm focus:outline-none transition-colors"
            />
            <button 
              type="submit"
              disabled={isTyping || !input.trim()}
              className="absolute right-2 top-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 rounded-md transition-colors flex items-center justify-center text-white"
            >
              <ChevronRight size={18} />
            </button>
          </form>
        </div>
      </div>

      {/* ================= SETTINGS MODAL ================= */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-[#161B22] border border-gray-800 p-6 rounded-xl w-[500px] shadow-2xl">
            <h2 className="text-xl font-bold mb-4 text-white">Engine Configuration</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Provider</label>
                <select 
                  value={settings.provider}
                  onChange={(e) => setSettings({...settings, provider: e.target.value})}
                  className="w-full bg-[#0D1117] border border-gray-700 rounded-md p-2 text-sm focus:border-blue-500 focus:outline-none"
                >
                  <option value="gemini">Google Gemini</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="ollama">Local Ollama</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Model Name</label>
                <input 
                  type="text" 
                  value={settings.model}
                  onChange={(e) => setSettings({...settings, model: e.target.value})}
                  className="w-full bg-[#0D1117] border border-gray-700 rounded-md p-2 text-sm focus:border-blue-500 focus:outline-none"
                />
              </div>

              {settings.provider !== "ollama" && (
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">API Key</label>
                  <input 
                    type="password" 
                    value={settings.api_key}
                    onChange={(e) => setSettings({...settings, api_key: e.target.value})}
                    placeholder="sk-..."
                    className="w-full bg-[#0D1117] border border-gray-700 rounded-md p-2 text-sm focus:border-blue-500 focus:outline-none"
                  />
                </div>
              )}

              {settings.provider === "ollama" && (
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Ollama Base URL</label>
                  <input 
                    type="text" 
                    value={settings.ollama_base_url}
                    onChange={(e) => setSettings({...settings, ollama_base_url: e.target.value})}
                    className="w-full bg-[#0D1117] border border-gray-700 rounded-md p-2 text-sm focus:border-blue-500 focus:outline-none"
                  />
                </div>
              )}
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <button 
                onClick={() => setShowSettings(false)}
                className="px-4 py-2 rounded-md hover:bg-gray-800 text-sm font-medium transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={saveSettings}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md text-sm font-medium transition-colors"
              >
                Save Configuration
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}