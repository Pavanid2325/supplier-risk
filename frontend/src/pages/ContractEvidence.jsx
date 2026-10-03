import React, { useState } from 'react';
import { FileText, Search, Lock, Layers } from 'lucide-react';

export default function ContractEvidence({ activeTenant }) {
  const [query, setQuery] = useState('insolvency liability SUP-40217');
  const [k, setK] = useState(3);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/tools/call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'search_contract_corpus',
          version: 'v1',
          inputs: { query: query, k: parseInt(k) }
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Search request failed');
      }

      const data = await res.json();
      setResults(data.result || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            Hybrid Contract Search & Clause Entitlement Explorer
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Combines TF-IDF vector similarity with keyword token overlap and Reciprocal Rank Fusion (RRF) ranking.
          </p>
        </div>

        <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Search Query
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm px-3.5 py-2 rounded-lg focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Top K Chunks
            </label>
            <input
              type="number"
              value={k}
              onChange={(e) => setK(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-cyan-400 text-sm px-3.5 py-2 rounded-lg focus:outline-none focus:border-cyan-500 font-mono"
              min="1"
              max="10"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm py-2.5 rounded-lg shadow-lg transition"
            >
              {loading ? 'Searching...' : 'Hybrid Search'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl text-xs font-mono">
          Search Error: {error}
        </div>
      )}

      {/* Results List */}
      <div className="space-y-3">
        {results.map((doc, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-2 shadow-md">
            <div className="flex justify-between items-start font-mono text-xs">
              <span className="text-cyan-400 font-bold text-sm">{doc.document_id} — {doc.section}</span>
              <div className="flex items-center gap-2">
                <span className="bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
                  RRF Score: {doc.score}
                </span>
                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                  Tenant: {doc.tenant_id}
                </span>
              </div>
            </div>
            <p className="text-xs text-slate-300 font-sans leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
              {doc.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
