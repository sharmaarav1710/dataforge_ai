import React, { useState } from 'react';
import { datasetApi } from '../api/dataset';

interface AIQueryPanelProps {
  datasetId: string;
  currentVersionId: string;
}

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

export const AIQueryPanel: React.FC<AIQueryPanelProps> = ({ datasetId, currentVersionId }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'ai', text: `✨ Connected to version ${currentVersionId}. Ask me anything about your data or request transformations like 'drop column [name]'!` }
  ]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !datasetId) return;

    const userMsg = query.trim();
    setQuery('');
    setMessages((prev) => [...prev, { sender: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await datasetApi.queryDatasetWithAI(datasetId, userMsg, currentVersionId);
      setMessages((prev) => [...prev, { sender: 'ai', text: res.answer || 'Query processed successfully.' }]);
    } catch (err) {
      setMessages((prev) => [...prev, { sender: 'ai', text: err instanceof Error ? err.detail || err.message : 'Failed to process AI query.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative group rounded-3xl p-[1px] bg-gradient-to-b from-indigo-500/30 via-slate-800 to-slate-900 shadow-2xl transition-all duration-300 hover:shadow-indigo-500/10">
      <div className="rounded-[23px] bg-slate-950/90 backdrop-blur-xl p-6 space-y-4">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-3">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
            </div>
            <h3 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
              DataForge Copilot <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">{currentVersionId}</span>
            </h3>
          </div>
          <span className="text-xs text-slate-400">Natural language data engineering</span>
        </div>

        {/* Message Log */}
        <div className="max-h-[280px] overflow-y-auto space-y-3 pr-2 scroll-smooth">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col transition-all duration-300 ${
                msg.sender === 'user' ? 'items-end' : 'items-start'
              }`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed whitespace-pre-wrap shadow-md ${
                  msg.sender === 'user'
                    ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-br-none shadow-indigo-600/20'
                    : 'bg-slate-900/90 text-slate-200 rounded-bl-none border border-slate-800'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex items-start animate-pulse">
              <div className="bg-slate-900 text-indigo-400 border border-slate-800 rounded-2xl rounded-bl-none px-4 py-2.5 text-xs flex items-center gap-2">
                <svg className="animate-spin h-3.5 w-3.5 text-indigo-400" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing data matrix & mutations...
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSubmit} className="flex gap-2 pt-2">
          <input
            type="text"
            placeholder="Ask a question or type mutation (e.g., 'Drop column age')..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            className="flex-1 rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 transition-all duration-200 focus:border-indigo-500 focus:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-indigo-600/20 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 transition-all duration-200 active:scale-95"
          >
            Send
          </button>
        </form>

      </div>
    </div>
  );
};