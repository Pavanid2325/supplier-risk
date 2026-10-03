import React from 'react';
import { Cpu, CheckCircle2, Clock, Hash } from 'lucide-react';

export default function ToolExecutionTrace({ trace = [], totalMs = 0 }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          Concurrent Tool Execution Trace
        </h4>
        <span className="text-xs font-mono bg-slate-800 text-cyan-400 px-2.5 py-1 rounded-full border border-slate-700">
          Total: {totalMs} ms (Concurrent)
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {trace.map((item, idx) => (
          <div key={idx} className="bg-slate-950 border border-slate-800 rounded-lg p-3 flex items-start justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-cyan-300 font-semibold">{item.tool}</span>
                <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono">
                  {item.version}
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-500" /> {item.execution_ms} ms
                </span>
                <span className="flex items-center gap-1 text-slate-400">
                  <Hash className="w-3 h-3 text-slate-500" /> Audit #{item.audit_seq}
                </span>
              </div>
            </div>
            <span className="inline-flex items-center gap-1 bg-emerald-500/10 text-emerald-400 text-[10px] px-2 py-0.5 rounded border border-emerald-500/20 font-semibold">
              <CheckCircle2 className="w-3 h-3" /> {item.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
