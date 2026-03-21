import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Activity, Layers3, PanelRightOpen, Radar, RefreshCw, ShieldCheck, Sparkles, Table2 } from 'lucide-react';
import EvoPyramid from './components/EvoPyramid';
import ArchitectTable from './components/ArchitectTable';
import SessionLauncher from './components/SessionLauncher';
import AgentWorkspace from './components/AgentWorkspace';
import KernelMonitor from './components/KernelMonitor';
import ObserverBanner from './components/ObserverBanner';
import NodeInspector from './components/NodeInspector';
import SwarmTerminalPanel from './components/SwarmTerminalPanel';
import ZBusAlert from './components/ZBusAlert';
import PyramidScene from './components/PyramidScene';

import { CORE_API_BASE } from './lib/config';
import { EvoNode } from './lib/evo';
import { useSwarmTerminal } from './lib/useSwarmTerminal';
import { usePyramidState } from './lib/usePyramidState';
import { AgentSession, useSessionRegistry } from './lib/useSessionRegistry';

type TabId = 'core' | 'nexus' | 'genesis' | 'table';
type ViewMode = 'structure' | 'directory' | 'active' | 'collaboration' | 'canon';

const PROVIDER_COLORS: Record<string, string> = {
  gpt: '#10a37f',
  gemini: '#4285f4',
  claude: '#f5a623',
  copilot: '#7c3aed',
  ollama: '#7c3aed',
  system: '#94a3b8',
};

const ACTIVE_SESSION_STATUSES: AgentSession['status'][] = ['active', 'waiting', 'review'];

const slugLabel = (value: string) => value.replace(/[^a-zA-Z0-9_-]+/g, '_').replace(/^_+|_+$/g, '') || 'node';
const normalizePath = (value: string) => value.replace(/\\/g, '/');

const nodeToPayload = (node: EvoNode) => ({
  id: node.id,
  title: node.label,
  summary: node.description ?? '',
  z_level: node.z,
  sector: node.sector.toUpperCase(),
  state: node.status,
  kind: node.kind,
  layer_type: node.layer,
  coords: { x: node.x, y: node.y, z: node.z },
  links: node.links,
  metadata: node.metadata ?? {},
});

const getProjectPathForNode = (node: EvoNode) => {
  const pathFromMetadata = node.metadata?.path;
  if (typeof pathFromMetadata === 'string' && pathFromMetadata.trim().length > 0) {
    return normalizePath(pathFromMetadata);
  }
  const layerFolder = node.z >= 11 ? 'α_Pyramid_Core' : node.z >= 5 ? 'β_Pyramid_Functional' : 'γ_Pyramid_Reflective';
  return `${layerFolder}/${node.sector.toUpperCase()}/${node.z}_${slugLabel(node.label ?? node.id)}`;
};

function App() {
  const { nodes: coreNodes, isConnected, latestZBusEvent, systemMetrics } = usePyramidState();
  const { events, connected: swarmConnected } = useSwarmTerminal();
  const { sessions, loadSessions } = useSessionRegistry();

  const [activeTab, setActiveTab] = useState<TabId>('core');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [assistantOpen, setAssistantOpen] = useState(true);
  const [showLauncher, setShowLauncher] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [panX, setPanX] = useState(50);
  const [panY, setPanY] = useState(50);
  const [activeZLevel, setActiveZLevel] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>('structure');
  const [syncingStructure, setSyncingStructure] = useState(false);
  const [guardingCanon, setGuardingCanon] = useState(false);
  const [showObserverBanner, setShowObserverBanner] = useState(true);
  
  const hasAutoSyncedRef = useRef(false);

  const dispatchKernelTask = useCallback(async (action: string, payload: any = {}) => {
    const envelope = {
      task_id: `ux-${Date.now()}`,
      source_node: 'EvoPyramid_UX_Core',
      target_node: 'gen-nexus',
      action: action,
      payload: payload,
      timestamp: new Date().toISOString(),
      metadata: { origin: 'ux-interface' }
    };

    const response = await fetch(`${CORE_API_BASE}/kernel/dispatch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(envelope),
    });

    if (!response.ok) {
      throw new Error(`Dispatch failed: ${response.statusText}`);
    }
    
    const result = await response.json();
    if (result.status === 'REJECTED') {
      throw new Error(`Kernel Rejected: ${result.reason}`);
    }
    return result;
  }, []);

  const syncNodeToCore = useCallback(async (node: EvoNode) => {
    return dispatchKernelTask('manifest_node', nodeToPayload(node));
  }, [dispatchKernelTask]);

  const baseNodes = useMemo(() => coreNodes, [coreNodes]);

  const sessionsByNode = useMemo(() => {
    const map = new Map<string, AgentSession[]>();
    sessions.forEach((session) => {
      const prev = map.get(session.node_id) ?? [];
      prev.push(session);
      map.set(session.node_id, prev);
    });
    map.forEach((value) => {
      value.sort((a, b) => b.updated_at.localeCompare(a.updated_at));
    });
    return map;
  }, [sessions]);

  const nodes = useMemo(() => {
    return baseNodes.map((node) => {
      const nodeSessions = sessionsByNode.get(node.id) ?? [];
      if (nodeSessions.length === 0) {
        return node;
      }
      const activeAgents = nodeSessions.slice(0, 4).map((session) => ({
        id: session.id,
        model: session.provider.toUpperCase(),
        color: PROVIDER_COLORS[session.provider] ?? '#94a3b8',
        task: session.task_title,
      }));
      return { ...node, activeAgents };
    });
  }, [baseNodes, sessionsByNode]);

  const selectedNode = useMemo(
    () => (selectedNodeId ? nodes.find((node) => node.id === selectedNodeId) ?? null : null),
    [nodes, selectedNodeId],
  );

  const selectedNodeSessions = useMemo(
    () => (selectedNode ? sessionsByNode.get(selectedNode.id) ?? [] : []),
    [selectedNode, sessionsByNode],
  );

  const activeSessionCount = useMemo(
    () => sessions.filter((session) => ACTIVE_SESSION_STATUSES.includes(session.status)).length,
    [sessions],
  );

  useEffect(() => {
    void loadSessions();
    const timer = window.setInterval(() => {
      void loadSessions();
    }, 3000);
    return () => clearInterval(timer);
  }, [loadSessions]);

  useEffect(() => {
    if (!activeSessionId && sessions.length > 0) {
      setActiveSessionId(sessions[0].id);
    }
  }, [activeSessionId, sessions]);

  useEffect(() => {
    if (!notice) {
      return;
    }
    const timer = window.setTimeout(() => setNotice(null), 3500);
    return () => clearTimeout(timer);
  }, [notice]);

  const [activeZBusEvent, setActiveZBusEvent] = useState<any>(null);

  useEffect(() => {
    if (latestZBusEvent) {
      setActiveZBusEvent(latestZBusEvent);
      const timer = window.setTimeout(() => {
        setActiveZBusEvent(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [latestZBusEvent]);

  const handleSessionCreated = (sessionId: string) => {
    setActiveSessionId(sessionId);
    setShowLauncher(false);
    setAssistantOpen(true);
    setNotice(`Session ${sessionId} is active`);
  };

  const handleManifestSelectedNode = async () => {
    if (!selectedNode) {
      return;
    }
    try {
      await syncNodeToCore(selectedNode);
      setNotice(`Manifested: ${getProjectPathForNode(selectedNode)}`);
    } catch {
      setNotice(`Manifest failed: ${selectedNode.id}`);
    }
  };

  const handleSyncFromStructure = useCallback(async () => {
    if (syncingStructure) {
      return;
    }

    setSyncingStructure(true);
    try {
      const data = await dispatchKernelTask('sync_structure', { update_existing: true });
      const stats = data.result || {};
      const added = Number(stats.added ?? 0);
      const updated = Number(stats.updated ?? 0);
      const scannedDirs = Number(stats.scanned_dirs ?? 0);
      setNotice(`Structure sync: +${added}, updated ${updated}, scanned ${scannedDirs}`);
    } catch (err: any) {
      setNotice(err.message || 'Structure sync failed');
    } finally {
      setSyncingStructure(false);
    }
  }, [syncingStructure, dispatchKernelTask]);

  const handleCanonGuard = useCallback(async () => {
    if (guardingCanon) {
      return;
    }

    setGuardingCanon(true);
    try {
      const data = await dispatchKernelTask('apply_canon_guard', { update_existing: true, prune_missing: false });
      const res = data.result || {};
      const sync = res.sync || {};
      const summary = res.guard?.summary || {};
      const added = Number(sync.added ?? 0);
      const updated = Number(sync.updated ?? 0);
      const drifted = Number(summary.drifted ?? 0);
      const missing = Number(summary.missing_in_state ?? 0);
      setNotice(`Canon guard: +${added}, updated ${updated}, drift ${drifted}, missing ${missing}`);
    } catch (err: any) {
      setNotice(err.message || 'Canon guard failed');
    } finally {
      setGuardingCanon(false);
    }
  }, [guardingCanon, dispatchKernelTask]);

  useEffect(() => {
    if (hasAutoSyncedRef.current) {
      return;
    }
    hasAutoSyncedRef.current = true;
    void handleSyncFromStructure();
  }, [handleSyncFromStructure]);

  const healthPct = systemMetrics?.health_pct !== undefined ? Math.round(systemMetrics.health_pct) : null;
  const memoryBlocks = systemMetrics?.memory_total ?? 0;

  return (
    <div className="app-shell flex h-screen text-slate-100 overflow-hidden">
      <main className={`pyramid-stage relative h-full transition-all duration-300 ${assistantOpen ? 'w-full lg:w-[60%]' : 'w-full'}`}>
        <header className="absolute top-0 left-0 right-0 z-40 px-4 md:px-6 py-4 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Radar className="w-4 h-4 text-emerald-400" />
              <h1 className="text-sm md:text-base font-semibold tracking-wide">EvoPyramid UX Core</h1>
            </div>
            <p className="text-[10px] text-slate-400 mt-0.5">Project structure + AI agent control from one interface</p>
          </div>

          <div className="flex items-center gap-2 md:gap-3">
            <KernelMonitor />
            
            {/* Universal LLM Metrics Widget */}
            {(healthPct !== null || memoryBlocks > 0) && (
              <div className="hidden md:flex items-center gap-3 text-[10px] px-3 py-1.5 rounded-full bg-black/40 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)] backdrop-blur">
                {healthPct !== null && (
                  <div className="flex items-center gap-1.5" title="System Health (ObserverRelay)">
                    <Activity className={`w-3.5 h-3.5 ${healthPct >= 90 ? 'text-emerald-400' : healthPct >= 60 ? 'text-amber-400' : 'text-rose-400'}`} />
                    <span className="font-mono text-slate-200">{healthPct}%</span>
                  </div>
                )}
                {healthPct !== null && memoryBlocks > 0 && <span className="text-slate-600">|</span>}
                {memoryBlocks > 0 && (
                  <div className="flex items-center gap-1.5" title="Cognitive Cortex Size (Blocks)">
                    <Layers3 className="w-3.5 h-3.5 text-blue-400" />
                    <span className="font-mono text-slate-200">{memoryBlocks} ENG</span>
                  </div>
                )}
              </div>
            )}

            <div className="hidden md:flex items-center gap-2 text-[10px] px-2 py-1 rounded-full bg-black/30 border border-white/10">
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'}`} />
              <span>CORE</span>
              <span className={`w-2 h-2 rounded-full ${swarmConnected ? 'bg-emerald-500' : 'bg-rose-500'}`} />
              <span>SWARM</span>
              <span className="text-slate-500">|</span>
              <span>{activeSessionCount} active</span>
              <span>{sessions.length} total</span>
            </div>
            <button
              onClick={() => setAssistantOpen(true)}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/15 border border-white/10"
              title="Open assistant"
            >
              <PanelRightOpen className="w-4 h-4" />
            </button>
          </div>
        </header>

        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-40 flex items-center gap-1 p-1 rounded-full bg-black/35 border border-white/10">
          <button
            onClick={() => {
              setActiveTab('core');
              setSelectedNodeId(null);
            }}
            className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 ${activeTab === 'core' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-white/10'}`}
          >
            <Layers3 className="w-3.5 h-3.5" />
            Core
          </button>
          <button
            onClick={() => {
              setActiveTab('genesis');
              setSelectedNodeId(null);
            }}
            className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 ${activeTab === 'genesis' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-white/10'}`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Genesis
          </button>
          <button
            onClick={() => {
              setActiveTab('nexus');
              setSelectedNodeId(null);
            }}
            className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 ${activeTab === 'nexus' ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:bg-white/10'}`}
          >
            <Radar className="w-3.5 h-3.5" />
            Nexus
          </button>
          <button
            onClick={() => {
              setActiveTab('table');
              setSelectedNodeId(null);
            }}
            className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 ${activeTab === 'table' ? 'bg-violet-600 text-white' : 'text-slate-300 hover:bg-white/10'}`}
          >
            <Table2 className="w-3.5 h-3.5" />
            Table
          </button>
        </div>

        <ObserverBanner 
          visible={showObserverBanner}
          onClose={() => setShowObserverBanner(false)}
          onNotice={setNotice}
          onInspectNode={setSelectedNodeId}
        />

        <ZBusAlert event={activeZBusEvent} />

        {activeTab === 'table' ? (
          <div className="h-full pt-24 pb-6 px-3 md:px-6">
            <ArchitectTable nodes={nodes} onSelectNode={(node) => setSelectedNodeId(node.id)} />
          </div>
        ) : activeTab === 'nexus' ? (
          <div className="h-full relative">
            <PyramidScene
              nodes={nodes}
              selectedNodeId={selectedNodeId}
              onSelectNode={setSelectedNodeId}
            />
          </div>
        ) : (
          <div className="h-full">
            <EvoPyramid
              nodes={nodes}
              onSelectNode={(node) => setSelectedNodeId(node?.id ?? null)}
              selectedNode={selectedNode}
              panX={panX}
              panY={panY}
              activeZLevel={activeZLevel}
              viewMode={viewMode}
            />
          </div>
        )}

        {activeTab !== 'table' && activeTab !== 'nexus' && (
          <>
            <div className="absolute left-4 top-1/2 -translate-y-1/2 z-30 hidden md:flex flex-col items-center gap-3 p-2 rounded-xl bg-black/30 border border-white/10 backdrop-blur">
              <input
                type="range"
                min={0}
                max={100}
                value={panY}
                onChange={(e) => {
                  setPanY(Number(e.target.value));
                  setActiveZLevel(0);
                }}
                aria-label="Pan Y"
                className="slider-vertical h-36 w-2"
              />
              <input
                type="range"
                min={0}
                max={17}
                step={1}
                value={activeZLevel}
                onChange={(e) => setActiveZLevel(Number(e.target.value))}
                aria-label="Z level"
                className="slider-vertical h-36 w-2"
              />
              <span className="text-[10px] font-mono text-slate-300">{activeZLevel === 0 ? 'ALL' : `Z${activeZLevel}`}</span>
            </div>

            <div className="absolute left-1/2 -translate-x-1/2 bottom-5 z-30 w-[45%] hidden md:block">
              <input
                type="range"
                min={0}
                max={100}
                value={panX}
                onChange={(e) => setPanX(Number(e.target.value))}
                aria-label="Pan X"
                className="w-full"
              />
            </div>

            <div className="absolute right-4 top-[118px] z-40 rounded-xl bg-black/30 border border-white/10 px-2 py-1.5 backdrop-blur">
              <div className="flex items-center gap-2">
                <select
                  value={viewMode}
                  title="Pyramid View Mode"
                  onChange={(e) => setViewMode(e.target.value as ViewMode)}
                  className="bg-transparent text-[11px] text-slate-200 outline-none"
                >
                  <option value="structure">Structure</option>
                  <option value="directory">Directory</option>
                  <option value="active">Active</option>
                  <option value="collaboration">Collaboration</option>
                  <option value="canon">Canon</option>
                </select>
                <button
                  onClick={() => {
                    void handleSyncFromStructure();
                  }}
                  disabled={syncingStructure}
                  className="px-2 py-1 rounded-md border border-emerald-500/30 bg-emerald-500/15 text-emerald-200 text-[10px] font-semibold inline-flex items-center gap-1 disabled:opacity-60"
                  title="Sync missing modules from project structure"
                >
                  <RefreshCw className={`w-3 h-3 ${syncingStructure ? 'animate-spin' : ''}`} />
                  {syncingStructure ? 'Syncing' : 'Sync'}
                </button>
                <button
                  onClick={() => {
                    void handleCanonGuard();
                  }}
                  disabled={guardingCanon}
                  className="px-2 py-1 rounded-md border border-blue-500/35 bg-blue-500/15 text-blue-200 text-[10px] font-semibold inline-flex items-center gap-1 disabled:opacity-60"
                  title="Canon guard: validate and align pyramid with folder structure"
                >
                  <ShieldCheck className={`w-3 h-3 ${guardingCanon ? 'animate-pulse' : ''}`} />
                  {guardingCanon ? 'Guarding' : 'Guard'}
                </button>
              </div>
            </div>
          </>
        )}

        {selectedNode && (
          <NodeInspector 
            node={selectedNode}
            sessions={selectedNodeSessions}
            onClose={() => setSelectedNodeId(null)}
            onActivateAgent={() => setShowLauncher(true)}
            onManifest={() => void handleManifestSelectedNode()}
            onOpenAssistant={() => setAssistantOpen(true)}
          />
        )}

        {notice && (
          <div className="absolute top-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full bg-slate-900 border border-emerald-500/30 text-[11px] flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            {notice}
          </div>
        )}

        <SwarmTerminalPanel 
          open={terminalOpen}
          connected={swarmConnected}
          events={events}
          onToggle={() => setTerminalOpen(!terminalOpen)}
        />
      </main>

      {assistantOpen && (
        <>
          <div className="fixed inset-0 z-30 bg-black/50 lg:hidden" onClick={() => setAssistantOpen(false)} />
          <aside className="fixed inset-y-0 right-0 z-40 w-full max-w-[460px] lg:static lg:max-w-none lg:w-[40%] border-l border-white/10">
            <AgentWorkspace
              sessionId={activeSessionId}
              onClose={() => setAssistantOpen(false)}
              onSessionChange={(sessionId) => setActiveSessionId(sessionId)}
            />
          </aside>
        </>
      )}

      {showLauncher && selectedNode && (
        <SessionLauncher node={selectedNode} onClose={() => setShowLauncher(false)} onCreated={handleSessionCreated} />
      )}
    </div>
  );
}

export default App;








