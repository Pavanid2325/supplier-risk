import React from 'react';
import { ShieldCheck, Database, Key, Activity, Lock } from 'lucide-react';

export default function Navbar({ activeTenant, setActiveTenant }) {
  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center justify-between sticky top-0 z-30 shadow-md">
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-tr from-cyan-600 to-emerald-500 p-2 rounded-lg text-slate-950 font-bold shadow-lg shadow-cyan-500/20">
          <ShieldCheck className="w-6 h-6 stroke-[2.5]" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
            SUPPLIER RISK PLATFORM
            <span className="bg-cyan-500/10 text-cyan-400 text-xs px-2 py-0.5 rounded border border-cyan-500/20 font-mono">
              MCP Agentic v1.0
            </span>
          </h1>
          <p className="text-xs text-slate-400">Secure Multi-Tenant MCP Supplier Exposure System</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Tenant Selector */}
        <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
          <Lock className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Active Tenant:</span>
          <select 
            value={activeTenant}
            onChange={(e) => setActiveTenant(e.target.value)}
            className="bg-transparent text-emerald-400 font-mono font-medium focus:outline-none cursor-pointer"
          >
            <option value="tenant-alpha" className="bg-slate-900 text-emerald-400">tenant-alpha (Primary)</option>
            <option value="tenant-beta" className="bg-slate-900 text-amber-400">tenant-beta (Isolated)</option>
            <option value="admin" className="bg-slate-900 text-purple-400">admin (SuperUser)</option>
          </select>
        </div>

        {/* System Status Pill */}
        <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs px-3 py-1.5 rounded-lg">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span className="font-semibold">MCP Dispatcher Active</span>
        </div>
      </div>
    </header>
  );
}
