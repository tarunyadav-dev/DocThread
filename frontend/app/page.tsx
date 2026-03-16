"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Database, Terminal, Search, Code, Info, Sparkles } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  isSearching?: boolean;
}

const API_BASE = "http://localhost:8000/api";

export default function PandasExpertChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Phase 1: Search Pulse
    setMessages(prev => [...prev, { role: 'assistant', content: "", isSearching: true }]);

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          framework_name: "pandas",
          model: "openrouter/auto"
        }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = "";

      // Phase 2: Switch to Stream
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1].isSearching = false;
        next[next.length - 1].isStreaming = true;
        return next;
      });

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        accumulatedContent += chunk;

        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].content = accumulatedContent;
          return newMessages;
        });
      }

      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1].isStreaming = false;
        return next;
      });

    } catch (error) {
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1].isSearching = false;
        next[next.length - 1].content = "⚠️  ERROR: Check Backend Connection.";
        return next;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0d1117] text-slate-300 font-mono overflow-hidden">
      
      {/* SIDEBAR */}
      <aside className="w-72 bg-[#010409] border-r border-slate-800 p-6 flex flex-col hidden lg:flex">
        <div className="flex items-center gap-3 mb-10">
          <div className="bg-emerald-600 p-2 rounded-lg shadow-lg shadow-emerald-900/20">
            <Database size={20} className="text-white" />
          </div>
          <h1 className="text-lg font-bold text-white tracking-widest uppercase">Pandas_DB</h1>
        </div>

        <nav className="space-y-8 flex-1">
          <div>
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em] mb-4">Pipeline</p>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between p-2 rounded bg-[#161b22] border border-slate-800">
                <span className="text-slate-500">Mode</span>
                <span className="text-emerald-500 font-bold">RAG_STRICT</span>
              </div>
            </div>
          </div>
        </nav>

        <div className="mt-auto border-t border-slate-800 pt-6 text-[11px] text-slate-500">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span>Status: Connected</span>
          </div>
        </div>
      </aside>

      {/* MAIN CHAT */}
      <main className="flex-1 flex flex-col bg-[#0d1117]">
        <div className="h-14 border-b border-slate-800 flex items-center px-8 bg-[#0d1117]/80 backdrop-blur-md">
          <Terminal size={14} className="text-emerald-500 mr-3" />
          <span className="text-xs font-bold text-slate-400 tracking-tighter">root@docthread:~/pandas_assistant</span>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-10 space-y-10 custom-scrollbar">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center opacity-20">
                <Search size={64} className="mb-4 text-slate-700" />
                <p className="text-xl font-bold tracking-widest">AWAITING_INPUT...</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              
<div className={`relative p-5 rounded-2xl border text-sm transition-all shadow-2xl
  ${msg.role === 'user' 
    ? 'bg-blue-600/5 border-blue-500/20 text-blue-50 rounded-tr-none' 
    : 'bg-[#161b22] border-slate-800 text-slate-200 rounded-tl-none'
  }`}>
  
  {msg.isSearching ? (
    <div className="flex items-center gap-3 text-emerald-500 animate-pulse py-2">
       <Search size={18} className="animate-spin-slow" />
       <span className="font-bold tracking-tight">VECTOR_DB_RETRIEVAL_IN_PROGRESS...</span>
    </div>
  ) : (
    /* --- PASTE THE NEW LOGIC HERE --- */
    <div className={`prose prose-invert max-w-none font-sans text-[15px] leading-relaxed`}>
      {msg.content.split('### 📑 DOCUMENTATION REFERENCE').map((part, i) => (
        i === 0 ? (
          <div key={i} className="mb-4 text-slate-300">
            {part.replace('### 🧠 EXPERT ANALYSIS', '').trim()}
          </div>
        ) : (
          <div key={i} className="mt-4 p-4 bg-black/40 border border-emerald-500/20 rounded-xl font-mono text-[12px] shadow-inner">
            <div className="text-emerald-500 font-bold mb-3 flex items-center gap-2 border-b border-emerald-500/10 pb-2">
              <Database size={14} /> 
              <span className="tracking-widest">DOC_TRACE_LOG</span>
            </div>
            <div className="text-slate-400 overflow-x-auto">
              {part.trim()}
            </div>
          </div>
        )
      ))}
    </div>
    /* --- END OF NEW LOGIC --- */
  )}

  {msg.isStreaming && <span className="inline-block w-2 h-4 ml-1 bg-emerald-500 animate-pulse align-middle" />}
</div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* INPUT DECK */}
        <div className="p-8 bg-gradient-to-t from-[#0d1117] to-transparent">
          <div className="max-w-4xl mx-auto">
            <div className="relative flex items-center bg-[#010409] border border-slate-800 rounded-2xl p-2 pr-4 focus-within:border-emerald-500/50 transition-all shadow-2xl">
              <div className="px-4 text-emerald-900 font-black text-xl select-none">{'>'}</div>
              <input 
                type="text"
                placeholder="Message Pandas Documentation..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                className="flex-1 bg-transparent py-4 text-white focus:outline-none placeholder:text-slate-800 text-sm"
              />
              <button onClick={handleSend} disabled={isLoading} className="text-emerald-500 disabled:opacity-20 hover:text-emerald-400 transition-colors">
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </main>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
        .animate-spin-slow { animation: spin 4s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}