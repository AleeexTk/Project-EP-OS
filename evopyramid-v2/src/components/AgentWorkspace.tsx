import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, CheckCircle, Database, Shield, Zap, X, Terminal, Clock, Send, Bot, Layers, FolderCheck, Cpu } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';
import { useSessionRegistry } from '../lib/useSessionRegistry';
import { usePyramidState } from '../lib/usePyramidState';
import FileExplorer from './FileExplorer';
import FileContentViewer from './FileContentViewer';

interface AgentWorkspaceProps {
  sessionId: string | null;
  onClose: () => void;
  onSessionChange?: (sessionId: string) => void;
}

const MessageRenderer = ({ msg }: { msg: any }) => {
  const isQuantumReq = msg.content.includes("QUANTUM SCENARIO PROTOCOL ACTIVATED");
  const isAssistant = msg.role === 'assistant';
  
  if (msg.role === 'user') {
    let displayContent = msg.content;
    if (isQuantumReq) {
      const taskMatch = displayContent.match(/TASK:\s*(.*)/s);
      displayContent = taskMatch ? `🌌 Quantum Task:\n${taskMatch[1]}` : displayContent;
    }
    return <div className="whitespace-pre-wrap">{displayContent}</div>;
  }

  if (isAssistant) {
    const synthesisMatch = msg.content.match(/(Final Synthesis|Verdict|Overseer Synthesis|Overseer Verdict).*?:?(.*)/si);
    if (synthesisMatch) {
        const branchesText = msg.content.substring(0, synthesisMatch.index);
        const synthesisText = synthesisMatch.input.substring(synthesisMatch.index + synthesisMatch[1].length).replace(/^[:\-\s]+/, '').trim();
        
        return (
          <div className="space-y-3 mt-1">
            {branchesText.trim() && (
              <div className="text-[11px] text-slate-400 bg-black/40 border border-white/5 rounded p-2 max-h-32 overflow-y-auto custom-scrollbar">
                <div className="text-[9px] uppercase tracking-wider text-slate-500 mb-1 border-b border-white/5 pb-1 flex justify-between">
                  <span>Tree of Thoughts (Branches)</span>
                  <span>⚙️</span>
                </div>
                <div className="whitespace-pre-wrap font-mono leading-relaxed">{branchesText.trim()}</div>
              </div>
            )}
            {synthesisText && (
              <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-3 text-purple-100 relative shadow-[0_0_15px_rgba(168,85,247,0.1)] mt-2">
                 <div className="absolute -top-2 -left-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-[9px] uppercase tracking-wider px-2 py-0.5 rounded shadow">🌌 Overseer Synthesis</div>
                 <div className="whitespace-pre-wrap mt-1">{synthesisText}</div>
              </div>
            )}
          </div>
        );
    }
  }
  return <div className="whitespace-pre-wrap">{msg.content}</div>;
};

export default function AgentWorkspace({ sessionId, onClose, onSessionChange }: AgentWorkspaceProps) {
  const { sessions, loadSessions, dispatchPrompt } = useSessionRegistry();
  const { latestZBusEvent } = usePyramidState();

  const [bridgeHealth, setBridgeHealth] = useState({
    status: 'WAITING FOR HEARTBEAT',
    provider: 'Unknown',
    tabAttached: false,
    authOk: false,
    lastHeartbeat: null as string | null,
    lastError: null as string | null,
    lastErrorTopic: null as string | null,
    severity: 'info'
  });

  const [streamData, setStreamData] = useState({
    active: false,
    content: '',
    latency: 0,
    startTime: 0,
    status: 'idle',
  });

  const [promptDraft, setPromptDraft] = useState('');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(sessionId || (sessions.length > 0 ? sessions[0].id : null));
  const [isQuantumMode, setIsQuantumMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'truth' | 'workspace'>('truth');
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [pendingMessages, setPendingMessages] = useState<any[]>([]);

  useEffect(() => { loadSessions(); }, []);
  useEffect(() => { if (sessionId && sessionId !== activeSessionId) setActiveSessionId(sessionId); }, [sessionId]);

  useEffect(() => {
    if (!latestZBusEvent) return;
    const { topic, payload } = latestZBusEvent;
    const timeStr = new Date().toLocaleTimeString();

    if (topic === 'BRIDGE_HEARTBEAT' || topic === 'BRIDGE_CONNECTED') {
      setBridgeHealth(prev => ({ ...prev, status: 'CONNECTED', lastHeartbeat: timeStr, provider: payload?.provider || 'ChatGPT', severity: 'info' }));
    } else if (topic === 'SESSION_ATTACHED' || topic === 'TAB_DISCOVERED') {
      setBridgeHealth(prev => ({ ...prev, tabAttached: true, provider: payload?.provider_id || 'ChatGPT', status: 'TAB BOUND', authOk: true }));
    } else if (['BRIDGE_ERROR', 'DOM_ERROR', 'AUTH_ERROR', 'SESSION_TAB_MISSING'].includes(topic)) {
      setBridgeHealth(prev => ({ ...prev, lastError: payload?.detail || topic, lastErrorTopic: topic, severity: 'error' }));
      if (streamData.active) setStreamData(prev => ({ ...prev, status: 'failed', active: false }));
    } else if (topic === 'PROMPT_DISPATCH' || topic === 'prompt.dispatch') {
        const prov = payload?.provider?.toLowerCase();
        if (prov === 'gemini' || prov === 'ollama') {
            setBridgeHealth(prev => ({ ...prev, status: 'DIRECT API', provider: prov.toUpperCase(), tabAttached: true, authOk: true, severity: 'info' }));
        }
    } else if (topic === 'PROMPT_ACCEPTED' || topic === 'SESSION_CREATED') {
      loadSessions();
      setBridgeHealth(prev => ({ ...prev, lastError: null, lastErrorTopic: null, severity: 'info' }));
      if (topic === 'PROMPT_ACCEPTED') {
          setStreamData({ active: true, content: '', latency: 0, startTime: Date.now(), status: 'running' });
      }
    } else if (topic === 'TOKEN_STREAM') {
      setStreamData(prev => ({ ...prev, active: true, status: 'running', content: payload?.content ?? (prev.content + (payload?.delta || '')) }));
    } else if (topic === 'RESPONSE_COMPLETE' || topic === 'SESSION_MESSAGE' || topic === 'SESSION_STATUS_CHANGED') {
      loadSessions();
      setPendingMessages([]); // Clear optimistic messages on sync
      if (topic === 'RESPONSE_COMPLETE') {
          setStreamData(prev => ({ ...prev, active: false, status: 'completed', content: payload?.content || prev.content, latency: prev.startTime > 0 ? Date.now() - prev.startTime : 0 }));
      }
    }
  }, [latestZBusEvent]);

  const handleDispatch = async () => {
    if (!promptDraft.trim() || !activeSessionId) return;
    
    // --- Optimistic UI Update ---
    const userPrompt = promptDraft.trim();
    setPromptDraft('');
    setPendingMessages(prev => [...prev, { id: 'pending-' + Date.now(), role: 'user', content: userPrompt }]);
    setStreamData({ active: true, content: '', latency: 0, startTime: Date.now(), status: 'running' });

    try {
      const data = await dispatchPrompt(activeSessionId, userPrompt, isQuantumMode ? 'quantum' : 'single');
      if (data?.status !== 'dispatched') {
          setBridgeHealth(prev => ({ ...prev, lastError: data?.errors?.join(', ') || 'API Dispatch Failed', severity: 'error' }));
          setStreamData(prev => ({ ...prev, active: false, status: 'failed' }));
          setPendingMessages(prev => prev.filter(m => !m.id.startsWith('pending-')));
      }
    } catch (e: any) {
      setBridgeHealth(prev => ({ ...prev, lastError: e.message, severity: 'error' }));
      setStreamData(prev => ({ ...prev, active: false, status: 'failed' }));
      setPendingMessages(prev => prev.filter(m => !m.id.startsWith('pending-')));
    }
  };

  const selectedSession = sessions.find(s => s.id === activeSessionId) || null;

  return (
    <section className="h-full bg-slate-950 text-slate-200 flex flex-col shadow-2xl overflow-y-auto no-scrollbar">
      <header className="px-4 py-3 flex items-center justify-between border-b border-white/10 bg-black/40 shrink-0">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400">Z-Bus Truth Layer</h2>
        </div>
        <div className="flex items-center gap-1 bg-black/50 p-1 rounded-md border border-white/5 mx-2">
            <button onClick={() => setActiveTab('truth')} className={`px-3 py-1 text-[10px] font-bold uppercase rounded transition-all ${activeTab === 'truth' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-500 hover:text-slate-300'}`}>Truth Layer</button>
            <button onClick={() => setActiveTab('workspace')} className={`px-3 py-1 text-[10px] font-bold uppercase rounded transition-all ${activeTab === 'workspace' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'text-slate-500 hover:text-slate-300'}`}>Workspace</button>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-white/10 rounded" title="Close Workspace Details"><X className="w-4 h-4 text-slate-500"/></button>
      </header>

      {activeTab === 'truth' ? (
        <div className="flex-1 p-4 space-y-4 overflow-y-auto custom-scrollbar">
          <div className={`p-3 rounded-lg border ${bridgeHealth.severity === 'error' ? 'border-rose-500/50 bg-rose-500/10' : 'border-emerald-500/30 bg-emerald-500/5'}`}>
            <div className="flex items-center gap-2 mb-2">
              <Activity className={`w-4 h-4 ${bridgeHealth.severity === 'error' ? 'text-rose-400' : 'text-emerald-400'}`} />
              <h3 className="text-xs font-bold uppercase tracking-wider">Bridge Health</h3>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
              <div className="text-slate-400">Status: <span className={bridgeHealth.status === 'CONNECTED' || bridgeHealth.status === 'TAB BOUND' ? 'text-emerald-400' : 'text-amber-400'}>{bridgeHealth.status}</span></div>
              <div className="text-slate-400">Provider: <span className="text-slate-200">{bridgeHealth.provider}</span></div>
              <div className="text-slate-400">Tab Attached: {bridgeHealth.tabAttached ? <span className="text-emerald-400">YES</span> : <span className="text-rose-400">NO</span>}</div>
              <div className="text-slate-400">Last Ping: <span className="text-slate-200">{bridgeHealth.lastHeartbeat || 'Never'}</span></div>
            </div>
          </div>

          <div className="p-3 rounded-lg border border-white/10 bg-black/30">
            <div className="flex items-center gap-2 mb-2 text-[10px] uppercase tracking-wider text-slate-500 font-bold">
              <Database className="w-3.5 h-3.5 text-blue-400" />
              Active Session
            </div>
            <select 
              aria-label="Select Active Session" 
              className="w-full bg-slate-900 border border-white/10 rounded p-1.5 text-xs text-slate-300 outline-none focus:border-emerald-500/50" 
              value={activeSessionId || ''} 
              onChange={(e) => { setActiveSessionId(e.target.value); if (onSessionChange) onSessionChange(e.target.value); }}
            >
              {sessions.map(s => {
                const color = s.provider === 'gpt' ? 'text-emerald-400' : 
                             s.provider === 'gemini' ? 'text-blue-400' :
                             s.provider === 'claude' ? 'text-amber-400' : 'text-slate-400';
                return (
                  <option key={s.id} value={s.id} className={color}>
                    {s.provider.toUpperCase()} - {s.task_title}
                  </option>
                );
              })}
            </select>
          </div>

          <div className="flex-1 flex flex-col border border-white/10 rounded-lg bg-black/30 overflow-hidden min-h-[300px]">
            <div className="p-2 border-b border-white/10 bg-black/40 flex items-center justify-between">
              <Bot className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold uppercase tracking-wider">Session History</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-4 text-sm">
              {selectedSession?.task_context && <div className="bg-emerald-950/20 border border-emerald-500/20 rounded-lg p-3 text-slate-300 text-xs"><div className="text-emerald-400 font-bold uppercase mb-1 flex items-center gap-1"><Shield className="w-3 h-3"/> Context</div>{selectedSession.task_context}</div>}
              {selectedSession?.messages?.map(msg => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-xl p-3 ${msg.role === 'user' ? 'bg-indigo-600/20 border border-indigo-500/30' : 'bg-slate-800/50 border border-white/5'}`}>
                    <MessageRenderer msg={msg} />
                  </div>
                </div>
              ))}
              {pendingMessages.map(msg => (
                <div key={msg.id} className="flex justify-end opacity-70 italic">
                  <div className="max-w-[85%] rounded-xl p-3 bg-indigo-600/10 border border-indigo-500/20">
                    <MessageRenderer msg={msg} />
                  </div>
                </div>
              ))}
              {streamData.active && <div className="flex justify-start"><div className="max-w-[85%] rounded-xl p-3 bg-slate-800/50 border border-emerald-500/30"><div className="text-[10px] text-emerald-400 mb-1 uppercase font-bold flex items-center gap-1"><Zap className="w-3 h-3 animate-pulse" /> Live Stream</div>{streamData.content || '...'}</div></div>}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col p-4 gap-4 overflow-hidden">
          <div className="flex-1 flex gap-4 min-h-0">
            <div className="w-1/3 min-w-[200px] flex flex-col"><FileExplorer onFileSelect={(path) => setSelectedPath(path)} /></div>
            <div className="flex-1 flex flex-col min-w-0">{selectedPath ? <FileContentViewer path={selectedPath} onClose={() => setSelectedPath(null)} onInject={(c) => setPromptDraft(prev => (prev ? prev + '\n\n' : '') + c)} /> : <div className="flex-1 flex flex-col items-center justify-center border border-white/5 rounded-lg bg-black/20 text-slate-600"><FolderCheck className="w-10 h-10 opacity-20 mb-2" /><div className="text-[11px] uppercase tracking-widest font-bold">Select File</div></div>}</div>
          </div>
          <div className="h-20 bg-blue-900/10 border border-blue-500/20 rounded-lg p-3 flex gap-4 shrink-0">
            <Cpu className="w-4 h-4 text-blue-400" />
            <div className="text-[11px] text-slate-400 leading-relaxed"><div className="text-blue-300 font-bold uppercase text-[10px]">Agent Context</div>System is scanning files. Agent has read access for analysis.</div>
          </div>
        </div>
      )}

      <div className="border-t border-white/10 bg-black/40 p-3 shrink-0">
        <textarea value={promptDraft} onChange={(e) => setPromptDraft(e.target.value)} placeholder="Type prompt..." className="w-full bg-transparent text-sm text-slate-200 outline-none resize-none" rows={2} />
        <div className="flex justify-between items-center mt-2 border-t border-white/10 pt-2">
          <div className="text-[10px] text-slate-500 font-mono flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              selectedSession?.provider === 'gpt' ? 'bg-emerald-500' :
              selectedSession?.provider === 'gemini' ? 'bg-blue-500' :
              selectedSession?.provider === 'claude' ? 'bg-amber-500' : 'bg-slate-500'
            }`} />
            Session: {selectedSession?.provider || 'none'}
            {selectedSession?.provider === 'gemini' || selectedSession?.provider === 'ollama' ? (
              <span className="text-[9px] bg-blue-500/10 text-blue-400 px-1 rounded border border-blue-500/20 ml-1">Direct API</span>
            ) : (
              <span className="text-[9px] bg-emerald-500/10 text-emerald-400 px-1 rounded border border-emerald-500/20 ml-1">Bridge Mode</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setIsQuantumMode(!isQuantumMode)} className={`px-2 py-1 text-[10px] uppercase font-bold rounded ${isQuantumMode ? "bg-purple-600/20 text-purple-400 border border-purple-500/50 shadow-[0_0_10px_rgba(168,85,247,0.4)]" : "bg-slate-800 text-slate-400"}`}>{isQuantumMode ? "🌌 Quantum" : "⚡ Fast"}</button>
            <button onClick={handleDispatch} disabled={!promptDraft.trim() || !activeSessionId || streamData.active} className="px-4 py-1 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-[11px] font-bold rounded transition-colors uppercase">Dispatch</button>
          </div>
        </div>
      </div>
    </section>
  );
}
