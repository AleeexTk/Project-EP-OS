import React, { useEffect, useState } from 'react';
import { ShieldAlert, Gavel, History, Trash2, CheckCircle2, XCircle, Bot, Wrench } from 'lucide-react';
import { CORE_API_BASE } from '../../lib/config';

interface AuditEvent {
  task_id: string;
  action: string;
  error: string;
  timestamp: string;
  source: string;
  target: string;
  origin_z: number;
}

interface AmnestyRecord {
  node_id: string;
  timestamp: string;
  reason: string;
  actor: string;
}

const AmnestyPanel: React.FC = () => {
  const [auditLog, setAuditLog] = useState<AuditEvent[]>([]);
  const [amnestyJournal, setAmnestyJournal] = useState<AmnestyRecord[]>([]);
  const [quarantinedNodes, setQuarantinedNodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [amnestyReason, setAmnestyReason] = useState('Manual Review: Structural Integrity Verified');
  const [activeSubTab, setActiveSubTab] = useState<'violations' | 'amnesty' | 'repairs'>('violations');
  const [repairHistory, setRepairHistory] = useState<any[]>([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [auditRes, amnestyRes, quarantineRes, repairRes] = await Promise.all([
        fetch(`${CORE_API_BASE}/policy/audit`),
        fetch(`${CORE_API_BASE}/policy/amnesty`),
        fetch(`${CORE_API_BASE}/policy/quarantine`),
        fetch(`${CORE_API_BASE}/policy/repairs`)
      ]);
      
      setAuditLog(await auditRes.json());
      setAmnestyJournal(await amnestyRes.json());
      setQuarantinedNodes(await quarantineRes.json());
      setRepairHistory(await repairRes.json());
    } catch (err) {
      console.error('Failed to fetch security data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const grantAmnesty = async (nodeId: string) => {
    try {
      const res = await fetch(`${CORE_API_BASE}/policy/amnesty`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          node_id: nodeId,
          reason: amnestyReason,
          actor: 'Pyramid_Admin'
        })
      });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error('Amnesty failed:', err);
    }
  };

  const clearAudit = async () => {
    if (!window.confirm('Are you sure you want to clear the audit log? This action is irreversible.')) return;
    try {
      await fetch(`${CORE_API_BASE}/policy/audit`, { method: 'DELETE' });
      fetchData();
    } catch (err) {
      console.error('Clear audit failed:', err);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-full text-blue-400 animate-pulse font-mono tracking-widest">
      CONNECTING TO IRON GUARDIAN...
    </div>
  );

  return (
    <div className="flex flex-col h-full space-y-6 p-2 overflow-hidden">
      {/* Header Section */}
      <div className="flex items-center justify-between bg-black/40 border border-white/10 p-4 rounded-xl backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-rose-500/20 rounded-lg">
            <ShieldAlert className="w-6 h-6 text-rose-500" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Security & Amnesty Hub</h2>
            <p className="text-xs text-rose-400 font-mono italic opacity-80 mt-1">
              Trinity Integrity Protocol V4.2
            </p>
          </div>
        </div>
        <button 
          onClick={clearAudit}
          className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-rose-500/20 border border-white/10 hover:border-rose-500/30 rounded-lg text-xs font-semibold text-slate-300 hover:text-rose-400 transition-all"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear Audit
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0 overflow-hidden">
        {/* Left Column: Active Sanctions */}
        <div className="flex flex-col space-y-4 min-h-0">
          <div className="flex items-center gap-2 text-rose-400 font-bold uppercase text-[10px] tracking-[0.2em]">
            <XCircle className="w-3 h-3" />
            Active Quarantined Nodes
          </div>
          <div className="flex-1 bg-black/30 border border-white/10 rounded-xl overflow-y-auto custom-scrollbar p-3 space-y-2">
            {quarantinedNodes.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-slate-500 italic text-sm">
                <CheckCircle2 className="w-10 h-10 mb-2 opacity-20" />
                No nodes in quarantine. System integrity optimal.
              </div>
            ) : (
              quarantinedNodes.map(nodeId => (
                <div key={nodeId} className="flex items-center justify-between p-3 bg-rose-500/5 border border-rose-500/20 rounded-lg group hover:border-rose-500/40 transition-all">
                  <div className="flex flex-col">
                    <span className="text-white font-mono text-sm">{nodeId}</span>
                    <span className="text-[10px] text-rose-400/60 uppercase">Sanctioned by Policy Manager</span>
                  </div>
                  <button 
                    onClick={() => grantAmnesty(nodeId)}
                    className="flex items-center gap-2 px-3 py-1 bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/30 rounded text-[10px] font-bold text-emerald-400 transition-all"
                  >
                    <Gavel className="w-3 h-3" />
                    GRANT AMNESTY
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="mt-2">
            <label 
              htmlFor="amnesty-rationale"
              className="text-[9px] text-slate-500 uppercase font-bold mb-1 block px-1"
            >
              Amnesty Rationale
            </label>
            <input 
              id="amnesty-rationale"
              type="text"
              placeholder="Enter reason for amnesty..."
              title="Amnesty Rationale"
              value={amnestyReason}
              onChange={(e) => setAmnestyReason(e.target.value)}
              className="w-full bg-black/40 border border-white/10 focus:border-emerald-500/50 rounded-lg px-3 py-2 text-xs text-white outline-none transition-all font-mono"
            />
          </div>
        </div>

        {/* Right Column: Audit/History Tabs */}
        <div className="flex flex-col space-y-4 min-h-0 overflow-hidden">
          <div className="flex items-center gap-4 border-b border-white/10 pb-1">
            <button 
              onClick={() => setActiveSubTab('violations')}
              className={`text-[10px] font-bold pb-2 px-1 tracking-widest uppercase flex items-center gap-2 transition-all ${activeSubTab === 'violations' ? 'text-blue-400 border-b-2 border-blue-500' : 'text-slate-500 hover:text-slate-300 border-b-2 border-transparent'}`}
            >
              <History className="w-3.5 h-3.5" />
              Violation Audit
            </button>
            <button 
              onClick={() => setActiveSubTab('amnesty')}
              className={`text-[10px] font-bold pb-2 px-1 tracking-widest uppercase flex items-center gap-2 transition-all ${activeSubTab === 'amnesty' ? 'text-emerald-400 border-b-2 border-emerald-500' : 'text-slate-500 hover:text-slate-300 border-b-2 border-transparent'}`}
            >
              <History className="w-3.5 h-3.5" />
              Amnesty History
            </button>
            <button 
              onClick={() => setActiveSubTab('repairs')}
              className={`text-[10px] font-bold pb-2 px-1 tracking-widest uppercase flex items-center gap-2 transition-all ${activeSubTab === 'repairs' ? 'text-amber-400 border-b-2 border-amber-500' : 'text-slate-500 hover:text-slate-300 border-b-2 border-transparent'}`}
            >
              <Wrench className="w-3.5 h-3.5" />
              Repair History
            </button>
          </div>

          {/* Combined Scrollable List */}
          <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1">
             {activeSubTab === 'violations' && auditLog.slice().reverse().map((event, idx) => (
               <div key={idx} className="p-3 bg-white/5 border border-white/10 rounded-lg text-xs group hover:bg-white/10 transition-all animate-in fade-in slide-in-from-right-2 duration-300">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono text-slate-500">{new Date(event.timestamp).toLocaleString()}</span>
                    <span className="px-1.5 py-0.5 bg-rose-500/10 text-rose-400 text-[9px] font-bold rounded uppercase border border-rose-500/20">{event.action}</span>
                  </div>
                  <div className="text-white font-mono mb-1 truncate">{event.source} {'->'} {event.target}</div>
                  <div className="text-rose-400/80 italic text-[10px] border-l-2 border-rose-500/40 pl-2 bg-rose-500/5 py-1 rounded-r">
                    {event.error}
                  </div>
               </div>
             ))}

             {activeSubTab === 'amnesty' && amnestyJournal.slice().reverse().map((record, idx) => (
               <div key={`amnesty-${idx}`} className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg text-xs group animate-in fade-in slide-in-from-right-2 duration-300">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono text-slate-500">{new Date(record.timestamp).toLocaleString()}</span>
                    <span className="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 text-[9px] font-bold rounded uppercase border border-emerald-500/30">AMNESTY</span>
                  </div>
                  <div className="text-white font-mono mb-1">Node: <span className="text-emerald-400">{record.node_id}</span></div>
                  <div className="text-slate-400 text-[10px]">
                    <span className="text-slate-500 uppercase font-bold text-[9px]">Reason: </span>
                    {record.reason}
                  </div>
                  <div className="text-slate-500 text-[9px] mt-1 italic text-right">Auth: {record.actor}</div>
               </div>
             ))}

             {activeSubTab === 'repairs' && repairHistory.slice().reverse().map((repair, idx) => (
               <div key={`repair-${idx}`} className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg text-xs group animate-in fade-in slide-in-from-right-2 duration-300">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono text-slate-500">{new Date(repair.timestamp).toLocaleString()}</span>
                    <span className="px-1.5 py-0.5 bg-amber-500/20 text-amber-400 text-[9px] font-bold rounded uppercase border border-amber-500/30">REPAIR</span>
                  </div>
                  <div className="text-white font-mono mb-1">Target: <span className="text-amber-400">{repair.node_id}</span></div>
                  <div className="text-slate-400 text-[10px] mb-2">
                    <span className="text-slate-500 uppercase font-bold text-[9px]">Diagnosis: </span>
                    {repair.reason}
                  </div>
                  <div className="p-2 bg-black/40 rounded border border-white/5 font-mono text-[9px] text-amber-200/70 whitespace-pre-wrap truncate max-h-20 overflow-hidden">
                    {repair.repaired_payload}
                  </div>
                  <div className="text-slate-500 text-[9px] mt-1 italic text-right flex items-center justify-end gap-1">
                    <Bot className="w-2.5 h-2.5 text-amber-500/50" />
                    Z14-Cortex ({repair.provider})
                  </div>
               </div>
             ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AmnestyPanel;
