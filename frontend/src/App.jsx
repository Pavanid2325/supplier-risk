import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import SupplierAnalysis from './pages/SupplierAnalysis';
import SupplierDetails from './pages/SupplierDetails';
import ContractEvidence from './pages/ContractEvidence';
import AuditLedger from './pages/AuditLedger';
import Evaluation from './pages/Evaluation';
import ToolRegistry from './pages/ToolRegistry';
import McpAppView from './components/McpAppView';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeTenant, setActiveTenant] = useState('tenant-alpha');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar activeTenant={activeTenant} setActiveTenant={setActiveTenant} />

      <div className="flex flex-1">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 p-8 max-w-7xl mx-auto overflow-y-auto">
          {activeTab === 'dashboard' && (
            <Dashboard setActiveTab={setActiveTab} activeTenant={activeTenant} />
          )}
          {activeTab === 'analysis' && (
            <SupplierAnalysis activeTenant={activeTenant} />
          )}
          {activeTab === 'suppliers' && (
            <SupplierDetails activeTenant={activeTenant} />
          )}
          {activeTab === 'mcp-app' && (
            <McpAppView activeTenant={activeTenant} />
          )}
          {activeTab === 'evidence' && (
            <ContractEvidence activeTenant={activeTenant} />
          )}
          {activeTab === 'ledger' && (
            <AuditLedger activeTenant={activeTenant} />
          )}
          {activeTab === 'evaluation' && (
            <Evaluation />
          )}
          {activeTab === 'tools' && (
            <ToolRegistry />
          )}
        </main>
      </div>
    </div>
  );
}
