import React, { useState, useEffect } from 'react';
import LedgerIntegrityBadge from '../components/LedgerIntegrityBadge';
import { History, ShieldCheck, ShieldAlert, Hash, Clock, Cpu } from 'lucide-react';

export default function AuditLedger({ activeTenant }) {
  const [entries, setEntries] = useState([]);
  const [ledgerStatus, setLedgerStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchLedgerData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/audit?limit=50');
      const data = await res.json();
      setEntries(data.entries || []);

      const verifyRes = await fetch('/api/audit/verify', { method: 'POST' });
      const verifyData = await verifyRes.json();
      setLedgerStatus(verifyData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLedgerData();
  }, [activeTenant]);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            Tamper-Evident SHA-256 Audit Ledger Chain
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            SQLite cryptographic ledger where every entry includes SHA-256 canonical payload hash linked to the previous entry hash.
          </p>
        </div>

        <LedgerIntegrityBadge 
          ledgerStatus={ledgerStatus}
          onVerify={fetchLedgerData}
          loading={loading}
        />
      </div>

      {/* Ledger Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950">
          <span className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
            Ledger Entries ({entries.length})
          </span>
          <span className="text-xs font-mono text-cyan-400">
            Hash Formula: SHA256(Payload + PrevHash)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-900 text-slate-400 font-mono border-b border-slate-800">
              <tr>
                <th className="p-3">Seq</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Tenant</th>
                <th className="p-3">Event</th>
                <th className="p-3">Tool</th>
                <th className="p-3">Entry Hash (SHA-256)</th>
                <th className="p-3">Previous Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
              {entries.map((item) => (
                <tr key={item.seq} className="hover:bg-slate-950/60">
                  <td className="p-3 text-cyan-400 font-bold">#{item.seq}</td>
                  <td className="p-3 text-slate-400">
                    {new Date(item.timestamp * 1000).toLocaleTimeString()}
                  </td>
                  <td className="p-3">{item.tenant_id}</td>
                  <td className="p-3">
                    <span className="bg-slate-800 px-2 py-0.5 rounded text-[10px] text-emerald-400 font-bold">
                      {item.event_type}
                    </span>
                  </td>
                  <td className="p-3 text-slate-200">{item.tool}</td>
                  <td className="p-3 font-mono text-[11px] text-cyan-300 truncate max-w-[140px]" title={item.entry_hash}>
                    {item.entry_hash.substring(0, 16)}...
                  </td>
                  <td className="p-3 font-mono text-[11px] text-slate-500 truncate max-w-[140px]" title={item.previous_hash}>
                    {item.previous_hash.substring(0, 16)}...
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
