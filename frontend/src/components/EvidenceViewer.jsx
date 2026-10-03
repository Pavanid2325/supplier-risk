import React from 'react';
import { FileText, ShieldAlert, Bookmark } from 'lucide-react';

export default function EvidenceViewer({ citations = [], warnings = [] }) {
  return (
    <div className="space-y-4">
      {/* Adversarial Contradiction Warning Box */}
      {warnings.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/30 text-amber-200 p-4 rounded-xl space-y-2">
          <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider text-amber-400">
            <ShieldAlert className="w-4 h-4" />
            Adversarial Defense Notice (Factual Precedence Override)
          </div>
          {warnings.map((warn, i) => (
            <p key={i} className="text-xs font-mono leading-relaxed bg-slate-950/60 p-2.5 rounded border border-amber-500/20">
              {warn}
            </p>
          ))}
        </div>
      )}

      {/* Citations List */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <Bookmark className="w-4 h-4 text-cyan-400" />
          Retrieved Contract Evidence & Citations ({citations.length})
        </h4>

        {citations.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No specific contract citations retrieved.</p>
        ) : (
          <div className="space-y-2.5">
            {citations.map((cite, idx) => (
              <div key={idx} className="bg-slate-950 border border-slate-800 p-3 rounded-lg text-xs space-y-1.5">
                <div className="flex items-center justify-between font-mono">
                  <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-slate-400" />
                    {cite.document_id} — {cite.section}
                  </span>
                  <span className="bg-slate-900 text-slate-400 px-2 py-0.5 rounded text-[10px] border border-slate-800">
                    Tenant: {cite.tenant_id}
                  </span>
                </div>
                <p className="text-slate-300 font-sans italic bg-slate-900/80 p-2 rounded border border-slate-800/80 text-[11px] leading-relaxed">
                  "{cite.snippet}"
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
