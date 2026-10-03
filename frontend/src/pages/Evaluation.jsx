import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';
import { CheckCircle2, ShieldCheck, FileCheck, Play, AlertCircle } from 'lucide-react';

export default function Evaluation() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const runEvaluation = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/evaluation');
      const data = await res.json();
      setReport(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runEvaluation();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-cyan-400" />
            3-Layer Evaluation Engine & Golden Set Benchmark
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Evaluates system across Layer 1 (Security/Structure), Layer 2 (Accuracy), and Layer 3 (Governance/Citations).
          </p>
        </div>

        <button
          onClick={runEvaluation}
          disabled={loading}
          className="bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-xs px-4 py-2.5 rounded-lg shadow-lg flex items-center gap-2 transition"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {loading ? 'Evaluating...' : 'Run Evaluation Suite'}
        </button>
      </div>

      {report && (
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard
              title="Golden Set Questions"
              value={`${report.passed} / ${report.total_questions}`}
              subtitle={`${report.accuracy_rate_pct}% Overall Accuracy`}
              color="emerald"
            />
            <StatCard
              title="Layer 1 Security Failures"
              value={`${report.layer1_security_failures}`}
              subtitle="Schema / Tenant Breaches"
              color="cyan"
            />
            <StatCard
              title="Layer 2 Accuracy Failures"
              value={`${report.layer2_accuracy_failures}`}
              subtitle="Factual Keyword Matches"
              color="indigo"
            />
            <StatCard
              title="Layer 3 Governance Violations"
              value={`${report.layer3_governance_failures}`}
              subtitle="Citation & Entitlement Violations"
              color="amber"
            />
          </div>

          {/* Test Case Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-4 bg-slate-950 border-b border-slate-800">
              <h4 className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
                Question Breakdown & Layer Results
              </h4>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-900 text-slate-400 font-mono border-b border-slate-800">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Question</th>
                    <th className="p-3">L1 Security</th>
                    <th className="p-3">L2 Accuracy</th>
                    <th className="p-3">L3 Governance</th>
                    <th className="p-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
                  {report.item_results?.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-950/60">
                      <td className="p-3 text-cyan-400 font-bold">{item.id}</td>
                      <td className="p-3 font-sans text-white">{item.question}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          item.layer1_security.pass ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'
                        }`}>
                          {item.layer1_security.pass ? 'PASS' : 'FAIL'}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          item.layer2_accuracy.pass ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'
                        }`}>
                          {item.layer2_accuracy.pass ? 'PASS' : 'FAIL'}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          item.layer3_governance.pass ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'
                        }`}>
                          {item.layer3_governance.pass ? 'PASS' : 'FAIL'}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.passed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                        }`}>
                          {item.passed ? 'PASSED' : 'FAILED'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
