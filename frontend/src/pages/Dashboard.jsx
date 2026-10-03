import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';
import LedgerIntegrityBadge from '../components/LedgerIntegrityBadge';
import { Building2, AlertTriangle, DollarSign, Layers, Wrench, ShieldCheck } from 'lucide-react';

export default function Dashboard({ setActiveTab, activeTenant }) {
  const [ledgerStatus, setLedgerStatus] = useState(null);
  const [loadingLedger, setLoadingLedger] = useState(false);

  const verifyLedger = async () => {
    setLoadingLedger(true);
    try {
      const res = await fetch('/api/audit/verify', { method: 'POST' });
      const data = await res.json();
      setLedgerStatus(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingLedger(false);
    }
  };

  useEffect(() => {
    verifyLedger();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            Supplier Exposure & Operational Risk Dashboard
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Real-time exposure monitoring backed by controlled MCP tool execution, hybrid TF-IDF contract retrieval, and SHA-256 tamper-evident ledger tracking.
          </p>
        </div>

        <LedgerIntegrityBadge 
          ledgerStatus={ledgerStatus}
          onVerify={verifyLedger}
          loading={loadingLedger}
        />
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Monitored Suppliers"
          value="4 Suppliers"
          subtitle="SUP-40217, SUP-51190, SUP-62001, SUP-73012"
          icon={Building2}
          color="cyan"
        />
        <StatCard
          title="Suppliers Requiring Review"
          value="1 High Risk"
          subtitle="SUP-40217 (>100k EUR balance)"
          icon={AlertTriangle}
          color="amber"
        />
        <StatCard
          title="Total Financial Exposure"
          value="€ 336,800.00"
          subtitle="Across all active ERP ledgers"
          icon={DollarSign}
          color="emerald"
        />
        <StatCard
          title="Alternative Sources"
          value="3 Sources"
          subtitle="Nordic SemiTech, Vanguard, Apex"
          icon={Layers}
          color="indigo"
        />
      </div>

      {/* Quick Action Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Risk Analysis Launcher */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-cyan-400" />
            Primary Supplier Analysis
          </h3>
          <p className="text-xs text-slate-400">
            Run multi-tool exposure query for <code className="text-cyan-400">SUP-40217</code> with automatic parallel dispatch.
          </p>
          <button
            onClick={() => setActiveTab('analysis')}
            className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs py-2.5 rounded-lg transition"
          >
            Analyze SUP-40217 Exposure →
          </button>
        </div>

        {/* Audit Verification Card */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Audit Ledger Integrity
          </h3>
          <p className="text-xs text-slate-400">
            Verify SHA-256 canonical hash links across all tenant execution records.
          </p>
          <button
            onClick={() => setActiveTab('ledger')}
            className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs py-2.5 rounded-lg border border-slate-700 transition"
          >
            View Full Audit Ledger →
          </button>
        </div>

        {/* Evaluation Benchmarks */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Wrench className="w-5 h-5 text-indigo-400" />
            3-Layer System Evaluation
          </h3>
          <p className="text-xs text-slate-400">
            Run 12 benchmark questions testing security, fact accuracy, and governance.
          </p>
          <button
            onClick={() => setActiveTab('evaluation')}
            className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs py-2.5 rounded-lg border border-slate-700 transition"
          >
            Run System Evaluation Suite →
          </button>
        </div>
      </div>
    </div>
  );
}
