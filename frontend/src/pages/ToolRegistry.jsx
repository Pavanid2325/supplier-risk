import React, { useState, useEffect } from 'react';
import { Wrench, Shield, Code, CheckCircle } from 'lucide-react';

export default function ToolRegistry() {
  const [tools, setTools] = useState([]);
  const [selectedTool, setSelectedTool] = useState(null);

  useEffect(() => {
    fetch('/api/tools')
      .then((res) => res.json())
      .then((data) => {
        setTools(data.tools || []);
        if (data.tools?.length > 0) setSelectedTool(data.tools[0]);
      });
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Wrench className="w-5 h-5 text-cyan-400" />
            Central MCP Tool Registry & Version Schemas
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Registered tools with required scope authorization and input JSON schemas.
          </p>
        </div>

        <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-3 py-1 rounded-full text-xs font-mono font-bold">
          {tools.length} Registered Tools
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Tool Cards */}
        <div className="space-y-3">
          {tools.map((t, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedTool(t)}
              className={`p-4 rounded-xl border cursor-pointer transition ${
                selectedTool?.name === t.name && selectedTool?.version === t.version
                  ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-400'
                  : 'bg-slate-900 border-slate-800 hover:border-slate-700 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between font-mono text-xs">
                <span className="font-bold text-white">{t.name}</span>
                <span className="bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded text-[10px]">
                  {t.version}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">{t.description}</p>
              <div className="mt-2 flex gap-1 flex-wrap">
                {t.required_scopes?.map((sc, i) => (
                  <span key={i} className="text-[10px] bg-slate-950 text-emerald-400 px-1.5 py-0.5 rounded font-mono border border-slate-800">
                    {sc}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Selected Tool Schema Detail */}
        {selectedTool && (
          <div className="md:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-start border-b border-slate-800 pb-3">
              <div>
                <span className="text-xs font-mono text-cyan-400 font-bold">{selectedTool.version}</span>
                <h3 className="text-xl font-bold text-white font-mono">{selectedTool.name}</h3>
              </div>
              <span className="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-1 rounded border border-emerald-500/20 font-semibold">
                Status: REGISTERED
              </span>
            </div>

            <p className="text-xs text-slate-300">{selectedTool.description}</p>

            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                Required JWT Scopes:
              </h4>
              <div className="flex gap-2">
                {selectedTool.required_scopes?.map((sc, i) => (
                  <span key={i} className="bg-slate-950 text-emerald-400 text-xs font-mono px-2.5 py-1 rounded border border-slate-800">
                    {sc}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Code className="w-3.5 h-3.5 text-cyan-400" />
                Input JSON Schema:
              </h4>
              <pre className="bg-slate-950 border border-slate-800 text-cyan-300 text-xs p-4 rounded-xl font-mono overflow-x-auto">
                {JSON.stringify(selectedTool.input_schema, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
