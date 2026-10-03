import React from 'react';
import { 
  LayoutDashboard, 
  Search, 
  Building2, 
  FileText, 
  History, 
  CheckCircle2, 
  Wrench,
  Monitor
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analysis', label: 'Supplier Risk Analysis', icon: Search },
    { id: 'suppliers', label: 'Supplier Details', icon: Building2 },
    { id: 'mcp-app', label: 'MCP Exposure App', icon: Monitor },
    { id: 'evidence', label: 'Contract Evidence', icon: FileText },
    { id: 'ledger', label: 'Audit Ledger', icon: History },
    { id: 'evaluation', label: 'System Evaluation', icon: CheckCircle2 },
    { id: 'tools', label: 'MCP Tool Registry', icon: Wrench },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-4 shrink-0 min-h-[calc(100vh-60px)]">
      <div className="space-y-1">
        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">Navigation</p>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="bg-slate-955 p-3 rounded-lg border border-slate-800/80 text-xs text-slate-400 space-y-1.5 font-mono">
        <div className="flex justify-between">
          <span className="text-slate-500">Security:</span>
          <span className="text-emerald-400">JWT Scopes Enforced</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Ledger:</span>
          <span className="text-cyan-400">SHA-256 Chained</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Retrieval:</span>
          <span className="text-indigo-400">TF-IDF + RRF</span>
        </div>
      </div>
    </aside>
  );
}
