import React from 'react';
import { ShieldCheck, ShieldX, RefreshCw } from 'lucide-react';

export default function LedgerIntegrityBadge({ ledgerStatus, onVerify, loading }) {
  if (!ledgerStatus) {
    return (
      <button 
        onClick={onVerify}
        disabled={loading}
        className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg font-medium transition"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        Verify Ledger Chain
      </button>
    );
  }

  const isValid = ledgerStatus.valid;

  return (
    <div className={`flex items-center gap-3 px-3.5 py-1.5 rounded-lg border text-xs font-mono ${
      isValid 
        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
        : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
    }`}>
      {isValid ? <ShieldCheck className="w-4 h-4" /> : <ShieldX className="w-4 h-4 animate-bounce" />}
      <div>
        <span className="font-bold uppercase">{isValid ? 'LEDGER VALID' : 'TAMPER DETECTED'}</span>
        <span className="mx-1.5 opacity-40">|</span>
        <span className="text-[11px]">{ledgerStatus.entries_checked} Entries Verified</span>
        {!isValid && (
          <span className="ml-2 bg-rose-500/20 px-1.5 py-0.5 rounded font-bold">
            First Bad Seq #{ledgerStatus.first_bad_seq}
          </span>
        )}
      </div>
      <button 
        onClick={onVerify}
        disabled={loading}
        className="ml-auto opacity-70 hover:opacity-100 transition"
      >
        <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
      </button>
    </div>
  );
}
