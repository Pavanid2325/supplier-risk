import React, { useState, useEffect } from 'react';
import { Building2, DollarSign, Calendar, Users, AlertCircle } from 'lucide-react';

export default function SupplierDetails({ activeTenant }) {
  const [selectedId, setSelectedId] = useState('SUP-40217');
  const [supplierData, setSupplierData] = useState(null);
  const [error, setError] = useState(null);

  const suppliersList = ['SUP-40217', 'SUP-51190', 'SUP-62001', 'SUP-73012'];

  const fetchDetails = async (id) => {
    setError(null);
    try {
      const res = await fetch(`/api/suppliers/${id}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to fetch supplier details');
      }
      const data = await res.json();
      setSupplierData(data);
    } catch (e) {
      setError(e.message);
      setSupplierData(null);
    }
  };

  useEffect(() => {
    fetchDetails(selectedId);
  }, [selectedId, activeTenant]);

  return (
    <div className="space-y-6">
      {/* Selector */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-cyan-400" />
            Supplier ERP Breakdown & Payment History
          </h2>
          <p className="text-xs text-slate-400 mt-1">Direct backend integration with synthetic ERP master ledger.</p>
        </div>

        <div className="flex gap-2">
          {suppliersList.map((id) => (
            <button
              key={id}
              onClick={() => setSelectedId(id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition ${
                selectedId === id
                  ? 'bg-cyan-500 text-slate-950 shadow-md'
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl text-xs font-mono flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>Tenant Isolation Security Block: {error}</span>
        </div>
      )}

      {supplierData && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex justify-between items-center">
            <div>
              <span className="text-xs font-mono text-cyan-400 font-semibold">{supplierData.supplier_id}</span>
              <h3 className="text-2xl font-bold text-white mt-0.5">{supplierData.name}</h3>
              <p className="text-xs text-slate-400 font-mono mt-1">Tenant Owner: {supplierData.tenant_id}</p>
            </div>

            <div className="text-right font-mono">
              <span className="text-xs text-slate-400">ERP Outstanding Balance:</span>
              <p className="text-2xl font-bold text-emerald-400">
                {supplierData.balance.currency} {supplierData.balance.owed_to_supplier.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Payment History Table */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-3">
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-400" />
              Monthly Payment Reliability History
            </h4>

            <div className="bg-slate-950 rounded-xl overflow-hidden border border-slate-800">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-900 text-slate-400 font-mono border-b border-slate-800">
                  <tr>
                    <th className="p-3">Month</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Delay Days</th>
                    <th className="p-3 text-right">Amount (EUR)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
                  {supplierData.payment_history?.map((pay, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/40">
                      <td className="p-3 font-semibold">{pay.month}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          pay.on_time ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          {pay.on_time ? 'ON TIME' : 'DELAYED'}
                        </span>
                      </td>
                      <td className="p-3">{pay.delay_days} days</td>
                      <td className="p-3 text-right">€ {pay.amount.toLocaleString()}</td>
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
