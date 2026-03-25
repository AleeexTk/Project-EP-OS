import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Sparkles } from 'lucide-react';
import EvoPyramid from './components/EvoPyramid';
import ArchitectTable from './components/ArchitectTable';
import SessionLauncher from './components/SessionLauncher';
import AgentWorkspace from './components/AgentWorkspace';
import NodeInspector from './components/NodeInspector';
import ObserverBanner from './components/ObserverBanner';
import SwarmTerminalPanel from './components/SwarmTerminalPanel';
import ZBusAlert from './components/ZBusAlert';
import PyramidScene from './components/PyramidScene';

// New Layout Components
import MainHeader from './components/Layout/MainHeader';
import NavigationTabs from './components/Layout/NavigationTabs';
import SidebarControls from './components/Layout/SidebarControls';
import AmnestyPanel from './components/Security/AmnestyPanel';

import { CORE_API_BASE } from './lib/config';
import { EvoNode } from './lib/evo';
import { useSwarmTerminal } from './lib/useSwarmTerminal';
import { usePyramidState } from './lib/usePyramidState';
import { PyramidProvider } from './lib/PyramidContext';
import { AgentSession, useSessionRegistry } from './lib/useSessionRegistry';

type TabId = 'core' | 'nexus' | 'genesis' | 'table' | 'security';
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
    try {
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
        throw new Error(`Dispatch failed: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      if (result.status === 'REJECTED' || result.status === 'FAILED') {
        throw new Error(`${result.metadata?.error || result.reason || 'Kernel Rejected'}`);
      }
      return result;
    } catch (err: any) {
      console.error(`[KERNEL_DISPATCH_ERROR] ${err.message}`);
      throw err;
    }
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
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(null), 4000);
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
    if (!selectedNode) return;
    try {
      await syncNodeToCore(selectedNode);
      setNotice(`Manifested: ${getProjectPathForNode(selectedNode)}`);
    } catch (err: any) {
      setNotice(`Manifest failed: ${err.message}`);
    }
  };

  const handleSyncFromStructure = useCallback(async () => {
    if (syncingStructure) return;
    setSyncingStructure(true);
    try {
      const data = await dispatchKernelTask('sync_structure', { update_existing: true });
      const stats = data.result || {};
      setNotice(`Structure sync: +${stats.added ?? 0}, updated ${stats.updated ?? 0}`);
    } catch (err: any) {
      setNotice(err.message || 'Structure sync failed');
    } finally {
      setSyncingStructure(false);
    }
  }, [syncingStructure, dispatchKernelTask]);

  const handleCanonGuard = useCallback(async () => {
    if (guardingCanon) return;
    setGuardingCanon(true);
    try {
      const data = await dispatchKernelTask('apply_canon_guard', { update_existing: true, prune_missing: false });
      const res = data.result || {};
      const sync = res.sync || {};
      const summary = res.guard?.summary || {};
      setNotice(`Canon guard: +${sync.added ?? 0}, update ${sync.updated ?? 0}, drift ${summary.drifted ?? 0}`);
    } catch (err: any) {
      setNotice(err.message || 'Canon guard failed');
    } finally {
      setGuardingCanon(false);
    }
  }, [guardingCanon, dispatchKernelTask]);

  useEffect(() => {
    if (hasAutoSyncedRef.current) return;
    hasAutoSyncedRef.current = true;
    void handleSyncFromStructure();
  }, [handleSyncFromStructure]);

  const healthPct = systemMetrics?.health_pct !== undefined ? Math.round(systemMetrics.health_pct) : null;
  const memoryBlocks = systemMetrics?.memory_total ?? 0;

  return (
    <div className="app-shell flex h-screen text-slate-100 overflow-hidden font-sans selection:bg-emerald-500/30">
      <main className={`pyramid-stage relative h-full transition-all duration-500 cubic-bezier(0.4, 0, 0.2, 1) ${assistantOpen ? 'w-full lg:w-[60%]' : 'w-full'}`}>
        
        <MainHeader 
          isConnected={isConnected}
          swarmConnected={swarmConnected}
          healthPct={healthPct}
          memoryBlocks={memoryBlocks}
          activeSessionCount={activeSessionCount}
          totalSessions={sessions.length}
          onOpenAssistant={() => setAssistantOpen(true)}
        />

        <NavigationTabs 
          activeTab={activeTab}
          onTabChange={(tab) => {
            setActiveTab(tab);
            setSelectedNodeId(null);
          }}
        />

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
        ) : activeTab === 'security' ? (
          <div className="h-full pt-24 pb-6 px-3 md:px-6 max-w-6xl mx-auto">
            <AmnestyPanel />
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

        {activeTab !== 'table' && activeTab !== 'nexus' && activeTab !== 'security' && (
          <SidebarControls 
            panX={panX}
            panY={panY}
            activeZLevel={activeZLevel}
            viewMode={viewMode}
            syncingStructure={syncingStructure}
            guardingCanon={guardingCanon}
            onPanXChange={setPanX}
            onPanYChange={(val) => {
              setPanY(val);
              setActiveZLevel(0);
            }}
            onZLevelChange={setActiveZLevel}
            onViewModeChange={setViewMode}
            onSync={handleSyncFromStructure}
            onGuard={handleCanonGuard}
          />
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
          <div className="absolute top-24 left-1/2 -translate-x-1/2 z-50 px-5 py-2.5 rounded-full bg-slate-900/90 border border-emerald-500/40 text-[11px] font-medium flex items-center gap-2 shadow-[0_4px_20px_rgba(16,185,129,0.2)] backdrop-blur animate-float">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="text-emerald-50 text-shadow-sm">{notice}</span>
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
          <div className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden transition-opacity duration-300" onClick={() => setAssistantOpen(false)} />
          <aside className="fixed inset-y-0 right-0 z-40 w-full max-w-[480px] lg:static lg:max-w-none lg:w-[40%] border-l border-white/10 bg-[#050b18]/80 backdrop-blur-xl shadow-[-10px_0_30px_rgba(0,0,0,0.5)]">
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

export default function WrappedApp() {
  return (
    <PyramidProvider>
      <App />
    </PyramidProvider>
  );
}








