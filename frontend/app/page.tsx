export default function Home() {
  return (
    <main className="flex h-screen bg-neutral-950 text-white p-4 gap-4">
      
      {/* Left Panel: Chat */}
      <div className="flex-1 border border-neutral-800 rounded-lg p-6 bg-neutral-900">
        <h1 className="text-xl font-bold mb-4 text-blue-400">DocThread AI</h1>
        <p className="text-neutral-400">I am ready to help you code.</p>
        
        {/* We will build the actual input box here later */}
        <div className="mt-8 p-4 bg-neutral-800 rounded text-sm text-neutral-500 border border-neutral-700">
          [ Chat Interface Goes Here ]
        </div>
      </div>

      {/* Right Panel: Documentation */}
      <div className="flex-1 border border-neutral-800 rounded-lg p-6 bg-neutral-900">
        <h1 className="text-xl font-bold mb-4 text-emerald-400">Source Docs</h1>
        <p className="text-neutral-400">Documentation will appear here.</p>
        
        {/* We will load the Markdown docs here later */}
        <div className="mt-8 p-4 bg-neutral-800 rounded text-sm text-neutral-500 border border-neutral-700">
          [ Traceability View Goes Here ]
        </div>
      </div>

    </main>
  );
}