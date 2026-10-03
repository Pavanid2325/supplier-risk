import React, { useState, useEffect } from 'react';
import { Monitor, DollarSign, Layers, AlertTriangle, ArrowRight } from 'lucide-react';

export default function McpAppView({ activeTenant }) {
  const [supplierId, setSupplierId] = useState('SUP-40217');
  const [resourceData, setResourceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchResource = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/mcp/resource?supplier_id=${id}`);
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to fetch MCP UI resource');
      }
      const data = await res.json();
      setResourceData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResource(supplierId);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Monitor className="w-5 h-5 text-cyan-400" />
            MCP App UI Resource: <code className="text-cyan-400 font-mono">ui://srp/supplier-exposure-view</code>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Standardized MCP interactive resource view dispatched through strict schema-validated API path.
          </p>
        </div>

        {/* Input Bar */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={supplierId}
            onChange={(e) => setSupplierId(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-cyan-400 font-mono text-sm px-3 py-1.5 rounded-lg focus:outline-none focus:border-cyan-500 w-36"
            placeholder="SUP-40217"
          />
          <button
            onClick={() => fetchResource(supplierId)}
            className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs px-4 py-2 rounded-lg transition"
          >
            Render Resource
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl text-xs font-mono">
          Security Rejection: {error}
        </div>
      )}

      {loading && (
        <div className="p-12 text-center text-slate-400 text-sm animate-pulse font-mono">
          Loading MCP UI Resource payload...
        </div>
      )}

      {resourceData && !loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-2xl">
          <div className="flex justify-between items-center border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs uppercase font-mono text-cyan-400 font-semibold tracking-wider">
                Supplier Exposure View
              </span>
              <h3 className="text-2xl font-bold text-white font-mono">{resourceData.supplier_id}</h3>
            </div>
            <span className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs px-3 py-1 rounded-full font-mono">
              Schema Validated
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Amount Owed */}
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-1">
              <span className="text-xs text-slate-400">Amount Owed (ERP):</span>
              <p className="text-xl font-bold text-emerald-400 font-mono">
                {resourceData.data.balance.currency} {resourceData.data.balance.owed_to_supplier?.toLocaleString()}
              </p>
            </div>

            {/* Alternates */}
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-1">
              <span className="text-xs text-slate-400">Alternative Sources:</span>
              <p className="text-xl font-bold text-cyan-400 font-mono">
                {resourceData.data.alternate_sources?.length || 0} Qualified
              </p>
            </div>

            {/* Payment History */}
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-1">
              <span className="text-xs text-slate-400">Payment Records:</span>
              <p className="text-xl font-bold text-amber-400 font-mono">
                {resourceData.data.payment_history?.length || 0} Cycles
              </p>
            </div>
          </div>

          {/* Alternate Suppliers Table */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Alternative Suppliers</h4>
            <div className="bg-slate-950 rounded-xl overflow-hidden border border-slate-800">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-900 text-slate-400 border-b border-slate-800 font-mono">
                  <tr>
                    <th className="p-3">Supplier ID</th>
                    <th className="p-3">Name</th>
                    <th className="p-3">Region</th>
                    <th className="p-3">Capacity</th>
                    <th className="p-3">Lead Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
                  {resourceData.data.alternate_sources?.map((alt, i) => (
                    <tr key={i} className="hover:bg-slate-900/50">
                      <td className="p-3 text-cyan-400 font-bold">{alt.supplier_id}</td>
                      <td className="p-3 text-white font-sans">{alt.name}</td>
                      <td className="p-3">{alt.region}</td>
                      <td className="p-3">{alt.capacity}</td>
                      <td className="p-3">{alt.lead_time_days} days</td>
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
