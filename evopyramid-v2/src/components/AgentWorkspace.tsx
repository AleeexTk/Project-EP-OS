import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, CheckCircle, Database, Shield, Zap, X, Terminal, Clock, Send, Bot } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';
import { useSessionRegistry } from '../lib/useSessionRegistry';
import { usePyramidState } from '../lib/usePyramidState';

interface AgentWorkspaceProps {
  sessionId: string | null;
  onClose: () => void;
  onSessionChange?: (sessionId: string) => void;
}

export default function AgentWorkspace({ sessionId, onClose, onSessionChange }: AgentWorkspaceProps) {
  const { sessions, loadSessions } = useSessionRegistry();
  const { latestZBusEvent } = usePyramidState();

  // Truth Layer States
  const [bridgeHealth, setBridgeHealth] = useState({
    status: 'WAITING FOR HEARTBEAT',
    provider: 'Unknown',
    tabAttached: false,
    authOk: false, // Assume false until proven
    lastHeartbeat: null as string | null,
    lastError: null as string | null,
    severity: 'info'
  });

  const [streamData, setStreamData] = useState({
    active: false,
    content: '',
    latency: 0,
    startTime: 0,
    status: 'idle', // idle | running | completed | failed
  });

  const [promptDraft, setPromptDraft] = useState('');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(sessionId || (sessions.length > 0 ? sessions[0].id : null));

  // Initialize and auto-refresh sessions
  useEffect(() => {
    loadSessions();
  }, []);

  // Update active session selection
  useEffect(() => {
    if (sessionId && sessionId !== activeSessionId) {
      setActiveSessionId(sessionId);
    }
  }, [sessionId]);

  // Handle incoming Z-Bus Truth
  useEffect(() => {
    if (!latestZBusEvent) return;
    const { topic, payload, severity } = latestZBusEvent;
    const timeStr = new Date().toLocaleTimeString();

    // 1. Bridge Health Updates
    if (topic === 'BRIDGE_HEARTBEAT') {
      setBridgeHealth(prev => ({ 
        ...prev, 
        status: 'CONNECTED', 
        lastHeartbeat: timeStr, 
        provider: payload?.provider || payload?.provider_id || 'ChatGPT', // Updated provider logic
        severity: 'info' 
      }));
    } else if (topic === 'SESSION_ATTACHED' || topic === 'TAB_DISCOVERED') {
      setBridgeHealth(prev => ({ 
        ...prev, 
        tabAttached: true, 
        provider: payload?.provider_id || 'ChatGPT',
        status: 'TAB BOUND'
      }));
    } else if (topic === 'BRIDGE_ERROR' || topic === 'DOM_ERROR') {
      setBridgeHealth(prev => ({ 
        ...prev, 
        lastError: payload?.detail || 'DOM/Bridge Error',
        severity: 'error'
      }));
      if (streamData.active) {
        setStreamData(prev => ({ ...prev, status: 'failed', active: false }));
      }
    } 
    // 2. Stream Updates
    else if (topic === 'PROMPT_ACCEPTED') {
      setStreamData({
        active: true,
        content: 'Waiting for tokens...',
        latency: 0,
        startTime: Date.now(),
        status: 'running'
      });
    } else if (topic === 'TOKEN_STREAM') {
      setStreamData(prev => ({
        ...prev,
        content: payload?.content || prev.content
      }));
    } else if (topic === 'RESPONSE_COMPLETE') {
      setStreamData(prev => {
        const lat = prev.startTime > 0 ? Date.now() - prev.startTime : 0;
        return {
          ...prev,
          active: false,
          content: payload?.content || prev.content,
          status: 'completed',
          latency: lat
        };
      });
    }
  }, [latestZBusEvent]);

  // Dispatch Prompt
  const handleDispatch = async () => {
    if (!promptDraft.trim() || !activeSessionId) return;

    setStreamData({ active: false, content: 'Dispatching...', latency: 0, startTime: 0, status: 'idle' });

    try {
      const response = await fetch(`${CORE_API_BASE}/v1/prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: promptDraft,
          session_ids: [activeSessionId],
          routing: 'single'
        })
      });
      const data = await response.json();
      if (data.status === 'dispatched') {
        setPromptDraft('');
      } else {
        setBridgeHealth(prev => ({ ...prev, lastError: 'API Dispatch Failed', severity: 'error' }));
      }
    } catch (e: any) {
      setBridgeHealth(prev => ({ ...prev, lastError: e.message, severity: 'error' }));
    }
  };

  const selectedSession = sessions.find(s => s.id === activeSessionId) || null;

  return (
    <section className="h-full bg-slate-950 text-slate-200 flex flex-col shadow-2xl overflow-y-auto no-scrollbar">
      {/* Header */}
      <header className="px-4 py-3 flex items-center justify-between border-b border-white/10 bg-black/40">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400">Z-Bus Truth Layer</h2>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-white/10 rounded" title="Close Workspace"><X className="w-4 h-4 text-slate-500"/></button>
      </header>

      <div className="p-4 space-y-4">
        
        {/* PANEL 1: BRIDGE HEALTH */}
        <div className={`p-3 rounded-lg border ${bridgeHealth.severity === 'error' ? 'border-rose-500/50 bg-rose-500/10' : 'border-emerald-500/30 bg-emerald-500/5'}`}>
          <div className="flex items-center gap-2 mb-2">
            <Activity className={`w-4 h-4 ${bridgeHealth.severity === 'error' ? 'text-rose-400' : 'text-emerald-400'}`} />
            <h3 className="text-xs font-bold uppercase tracking-wider">Bridge Health</h3>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
            <div className="text-slate-400">Status: <span className={bridgeHealth.status === 'CONNECTED' ? 'text-emerald-400' : 'text-amber-400'}>{bridgeHealth.status}</span></div>
            <div className="text-slate-400">Provider: <span className="text-slate-200">{bridgeHealth.provider}</span></div>
            <div className="text-slate-400">Tab Attached: {bridgeHealth.tabAttached ? <span className="text-emerald-400">YES</span> : <span className="text-rose-400">NO</span>}</div>
            <div className="text-slate-400">Last Ping: <span className="text-slate-200">{bridgeHealth.lastHeartbeat || 'Never'}</span></div>
          </div>
          {bridgeHealth.lastError && (
            <div className="mt-2 text-[10px] text-rose-300 bg-rose-950/50 p-1.5 rounded border border-rose-500/20 font-mono">
              ERR: {bridgeHealth.lastError}
            </div>
          )}
        </div>

        {/* PANEL 2: SESSIONS */}
        <div className="p-3 rounded-lg border border-white/10 bg-black/30">
          <div className="flex items-center gap-2 mb-2">
            <Database className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider">Active Sessions</h3>
          </div>
          <select 
            className="w-full bg-slate-900 border border-white/10 rounded p-1.5 text-xs text-slate-300 outline-none"
            value={activeSessionId || ''}
            title="Select Active Agent Session"
            onChange={(e) => {
              setActiveSessionId(e.target.value);
              if (onSessionChange) onSessionChange(e.target.value);
            }}
          >
            {sessions.map(s => (
              <option key={s.id} value={s.id}>{s.provider.toUpperCase()} - {s.task_title} [{s.status}]</option>
            ))}
          </select>
          {selectedSession && (
            <div className="mt-2 text-[10px] font-mono text-slate-500">
              ID: {selectedSession.id}<br/>
              Bridge Mode: {selectedSession.bridge_mode}<br/>
              Status: {selectedSession.status}
            </div>
          )}
        </div>

        {/* PANEL 3: RESPONSE STREAM VIEW */}
        <div className="p-3 rounded-lg border border-white/10 bg-black/30 flex-1 min-h-[150px] flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Zap className={`w-4 h-4 ${streamData.active ? 'text-amber-400 animate-pulse' : 'text-slate-400'}`} />
              <h3 className="text-xs font-bold uppercase tracking-wider">Live Stream</h3>
            </div>
            {streamData.status !== 'idle' && (
              <div className="flex items-center gap-2 text-[9px] font-mono">
                <span className={`${streamData.status === 'completed' ? 'text-emerald-400' : streamData.status === 'failed' ? 'text-rose-400' : 'text-amber-400'}`}>
                  [{streamData.status.toUpperCase()}]
                </span>
                {streamData.latency > 0 && <span className="text-slate-500">{streamData.latency}ms</span>}
              </div>
            )}
          </div>
          <div className="flex-1 bg-slate-950 rounded border border-white/5 p-2 overflow-y-auto text-xs whitespace-pre-wrap text-slate-300 font-sans">
            {streamData.content || (
              <span className="text-slate-600 italic">No active stream...</span>
            )}
          </div>
        </div>

        {/* PANEL 4: PROMPT CONSOLE */}
        <div className="border border-white/10 rounded-lg bg-black/40 p-2">
          <textarea
            value={promptDraft}
            onChange={(e) => setPromptDraft(e.target.value)}
            placeholder="Initialize Z-Bus Prompt Dispatch..."
            className="w-full bg-transparent text-sm text-slate-200 outline-none resize-none p-1"
            rows={3}
          />
          <div className="flex justify-between items-center mt-2 border-t border-white/10 pt-2">
            <span className="text-[10px] text-slate-500 font-mono">Target: {selectedSession?.provider || 'none'}</span>
            <button 
              onClick={handleDispatch}
              disabled={!promptDraft.trim() || !activeSessionId || streamData.active}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 rounded text-[11px] font-bold transition-colors"
            >
              <Send className="w-3 h-3" />
              DISPATCH
            </button>
          </div>
        </div>

      </div>
    </section>
  );
}
