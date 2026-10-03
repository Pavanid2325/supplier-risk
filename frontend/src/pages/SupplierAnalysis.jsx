import React, { useState } from 'react';
import ToolExecutionTrace from '../components/ToolExecutionTrace';
import EvidenceViewer from '../components/EvidenceViewer';
import { Search, ShieldAlert, Cpu, CheckCircle2, DollarSign, Layers, Clock } from 'lucide-react';

export default function SupplierAnalysis({ activeTenant }) {
  const [supplierId, setSupplierId] = useState('SUP-40217');
  const [question, setQuestion] = useState('Are we exposed if SUP-40217 fails?');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_id: supplierId,
          question: question
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Analysis request failed');
      }

      const data = await res.json();
      setAnalysisResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Search className="w-5 h-5 text-cyan-400" />
            Supplier Risk Analysis Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Enforces regex schema <code className="text-cyan-400 font-mono">^SUP-[0-9]&#123;5&#125;$</code> and dispatches concurrent tool execution.
          </p>
        </div>

        <form onSubmit={handleAnalyze} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Supplier ID
            </label>
            <input
              type="text"
              value={supplierId}
              onChange={(e) => setSupplierId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-cyan-400 font-mono text-sm px-3.5 py-2 rounded-lg focus:outline-none focus:border-cyan-500"
              placeholder="SUP-40217"
            />
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Risk Question
            </label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm px-3.5 py-2 rounded-lg focus:outline-none focus:border-cyan-500"
              placeholder="Are we exposed if SUP-40217 fails?"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-extrabold text-sm py-2.5 rounded-lg shadow-lg shadow-cyan-500/20 transition disabled:opacity-50"
            >
              {loading ? 'Executing Tools...' : 'Analyze Risk'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl text-xs font-mono">
          Security Rejection Error: {error}
        </div>
      )}

      {/* Analysis Output */}
      {analysisResult && !loading && (
        <div className="space-y-6">
          {/* Concise Answer Banner */}
          <div className="bg-slate-900 border border-cyan-500/30 p-6 rounded-2xl space-y-3 shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-mono text-cyan-400 font-semibold uppercase tracking-wider">
                Grounded Risk Synthesis Result
              </span>
              <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 px-2.5 py-0.5 rounded border border-emerald-500/20">
                Confidence: {Math.round(analysisResult.confidence_score * 100)}%
              </span>
            </div>

            <p className="text-base font-medium text-white leading-relaxed font-sans">
              {analysisResult.concise_answer}
            </p>

            {/* Key Findings List */}
            <div className="space-y-1.5 pt-2">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Key Grounded Findings:</h4>
              <ul className="space-y-1">
                {analysisResult.key_findings.map((finding, idx) => (
                  <li key={idx} className="text-xs text-slate-300 flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Concurrent Execution Trace Timeline */}
          <ToolExecutionTrace 
            trace={analysisResult.tool_execution_summary.trace}
            totalMs={analysisResult.tool_execution_summary.trace.reduce((acc, curr) => Math.max(acc, curr.execution_ms), 0)}
          />

          {/* Evidence Citations & Adversarial Warnings */}
          <EvidenceViewer 
            citations={analysisResult.citations}
            warnings={analysisResult.adversarial_warnings}
          />
        </div>
      )}
    </div>
  );
}
