import React, { useState, useEffect, useRef, useMemo } from 'react';
import EvoPyramid from './components/EvoPyramid';
import SessionLauncher from './components/SessionLauncher';
import AgentWorkspace from './components/AgentWorkspace';
import { EvoNode, STATUS_COLORS, SECTOR_COLORS } from './lib/evo';
import { usePyramidState } from './lib/usePyramidState';
import { useSwarmTerminal, SwarmEvent } from './lib/useSwarmTerminal';
import {
  MoreVertical, MessageSquare, Settings, Eye,
  SlidersHorizontal, Layers, X, ExternalLink,
  Terminal, Network, Wifi, WifiOff, Plus, Bot,
  Loader2, Maximize2, Minimize2, ChevronLeft, ChevronRight, Sparkles
} from 'lucide-react';

// ─── Provider color map ──────────────────────────────────────────────────────
const PROVIDER_COLORS: Record<string, string> = {
  gpt: '#10a37f',
  gemini: '#4285f4',
  claude: '#f5a623',
  copilot: '#7c3aed',
  ollama: '#7c3aed',
  system: '#94a3b8',
};

function EventRow({ ev }: { ev: SwarmEvent }) {
  const time = new Date(ev.ts).toLocaleTimeString('uk', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const color = PROVIDER_COLORS[ev.provider ?? 'system'] ?? '#94a3b8';
  const isSystem = ev.event === 'system';

  if (isSystem) {
    return (
      <div className="flex gap-2 text-slate-500 italic">
        <span className="shrink-0">[{time}]</span>
        <span>{ev.content}</span>
      </div>
    );
  }

  const label =
    ev.event === 'session.created' ? `→ Session bound to ${ev.node_id} (Z${ev.node_z})` :
      ev.event === 'session.message' ? `💬 ${ev.role}: ${ev.content}` :
        ev.event === 'session.status_changed' ? `Status → ${ev.new_status}` :
          ev.content ?? ev.event;

  return (
    <div className="flex gap-2">
      <span className="text-slate-500 shrink-0">[{time}]</span>
      <span className="font-bold shrink-0" data-provider={ev.provider ?? 'sys'}>{(ev.provider ?? 'sys').toUpperCase()}</span>
      <span className="text-slate-300">{label}</span>
    </div>
  );
}

import ArchitectTable from './components/ArchitectTable';

function App() {
  const { nodes: coreNodes, isConnected } = usePyramidState();
  const { events, connected: swarmConnected, sendCommand } = useSwarmTerminal();

  const [activeTab, setActiveTab] = useState<'core' | 'genesis' | 'table'>('core');

  // Child Pyramid: EvoGenesis (Aligned with evopyramid-ai and Nexus architecture)
  const genesisNodes: any[] = useMemo(() => [
    { id: 'gen-nexus', label: 'GLOBAL NEXUS', description: 'Z17 · Master Orchestration Layer (EvoGenesis)', z: 17, x: 9, y: 9, sector: 'SPINE', color: '#10b981', status: 'active', kind: 'service' },
    { id: 'gen-meta', label: 'EVO-META', description: 'Z15 · Self-Governance and Evolution Policy', z: 15, x: 9, y: 9, sector: 'PURPLE', color: '#a855f7', status: 'active', kind: 'protocol' },
    { id: 'gen-bridge', label: 'EVO-BRIDGE', description: 'Z13 · External Adapters (Replicate, GCP, OpenAI)', z: 13, x: 9, y: 9, sector: 'RED', color: '#ef4444', status: 'active', kind: 'agent' },
    { id: 'gen-pear', label: 'PEAR LOOP', description: 'Z11 · Perception-Evolution-Action-Reflection', z: 11, x: 9, y: 9, sector: 'GOLD', color: '#f59e0b', status: 'active', kind: 'memory' },
    { id: 'gen-async-jobs', label: 'ASYNC JOB RUNNER', description: 'Z9 · GCP/Replicate Task Queue (Polling/Pushing)', z: 9, x: 9, y: 9, sector: 'GREEN', color: '#10b981', status: 'active', kind: 'runtime' },
    { id: 'gen-webmcp', label: 'WEB MCP CORE', description: 'Z7 · Genesis Core Runtime & Web Components', z: 7, x: 9, y: 9, sector: 'GREEN', color: '#10b981', status: 'active', kind: 'runtime' },
    { id: 'gen-dashboard', label: 'EVO-DASHBOARD', description: 'Z5 · Integrated Environment Interface', z: 5, x: 9, y: 9, sector: 'SPINE', color: '#64748b', status: 'active', kind: 'service' },
  ], []);

  // Sync Genesis nodes with backend when first accessed
  useEffect(() => {
    if (activeTab === 'genesis') {
      genesisNodes.forEach(node => {
        // Send to core_engine to trigger folder manifestation
        fetch('http://127.0.0.1:8000/node', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: node.id,
            title: node.label,
            summary: node.description,
            z_level: node.z,
            sector: node.sector,
            state: node.status,
            kind: node.kind,
            layer_type: node.z >= 11 ? 'alpha' : node.z >= 5 ? 'beta' : 'gamma',
            coords: { x: node.x, y: node.y, z: node.z }
          })
        }).catch(err => console.error("Sync error:", err));
      });
    }
  }, [activeTab, genesisNodes]);

  const nodes = (activeTab === 'core' || activeTab === 'table')
    ? coreNodes
    : coreNodes.filter(n => n.id.startsWith('gen-')).length > 0 ? coreNodes.filter(n => n.id.startsWith('gen-')) : genesisNodes;

  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [workspaceOpen, setWorkspaceOpen] = useState(false);

  const [panY, setPanY] = useState(50);
  const [panX, setPanX] = useState(50);
  const [activeZLevel, setActiveZLevel] = useState<number>(0);
  const [viewMode, setViewMode] = useState<string>('structure');
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [showLauncher, setShowLauncher] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [events]);

  const notify = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 4000);
  };

  const handleSessionCreated = (id: string) => {
    setShowLauncher(false);
    setActiveSessionId(id);
    setWorkspaceOpen(true);
    notify(`Agent session ${id} activated in Native Workspace`);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans w-full">
      {/* ── LEFT ZONE: THE PYRAMID (WIDGET PART) ── */}
      <div className={`relative h-full transition-all duration-500 ease-in-out ${workspaceOpen ? 'w-[40%]' : 'w-full'}`}>

        {/* Connection Status */}
        <div className="absolute top-6 right-6 z-50 flex items-center gap-2 px-3 py-1.5 bg-white/10 backdrop-blur-md rounded-full border border-white/5">
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-[9px] font-bold text-slate-400 uppercase">CORE</span>
          </div>
          <div className="w-px h-3 bg-white/10" />
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${swarmConnected ? 'bg-emerald-400' : 'bg-red-500'}`} />
            <span className="text-[9px] font-bold text-slate-400 uppercase">Z9</span>
          </div>
        </div>

        {/* Tab Switching UI */}
        <div className="absolute top-6 left-1/2 -translate-x-1/2 z-50 flex gap-1 p-1 bg-black/40 backdrop-blur-md rounded-full border border-white/10 shadow-2xl">
          <button
            onClick={() => { setActiveTab('core'); setSelectedNode(null); }}
            className={`px-6 py-2 rounded-full text-xs font-bold transition-all duration-300 ${activeTab === 'core' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'text-white/50 hover:text-white hover:bg-white/5'}`}
          >
            MAIN CORE
          </button>
          <button
            onClick={() => { setActiveTab('genesis'); setSelectedNode(null); }}
            className={`px-6 py-2 rounded-full text-xs font-bold transition-all duration-300 ${activeTab === 'genesis' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/30' : 'text-white/50 hover:text-white hover:bg-white/5'}`}
          >
            EVOGENESIS
          </button>
          <button
            onClick={() => { setActiveTab('table'); setSelectedNode(null); }}
            className={`px-6 py-2 rounded-full text-xs font-bold transition-all duration-300 ${activeTab === 'table' ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/30' : 'text-white/50 hover:text-white hover:bg-white/5'}`}
          >
            TABLE VIEW
          </button>
        </div>

        {/* Content Area (Pyramid or Table) */}
        {activeTab === 'table' ? (
          <div className="flex-1 p-20 pt-28 h-full">
            <ArchitectTable nodes={nodes} onSelectNode={setSelectedNode} />
          </div>
        ) : (
          <div className="flex-1 h-full">
            <EvoPyramid
              nodes={nodes}
              onSelectNode={setSelectedNode}
              selectedNode={selectedNode}
              panX={panX}
              panY={workspaceOpen ? 50 : panY}
              activeZLevel={activeZLevel}
              viewMode={viewMode}
            />
          </div>
        )}

        {/* Floating Menu Toggle */}
        {!workspaceOpen && activeSessionId && (
          <button
            onClick={() => setWorkspaceOpen(true)}
            className="absolute right-6 top-20 z-40 p-3 bg-emerald-500 text-white rounded-full shadow-lg hover:bg-emerald-600 transition-all"
            title="Open Workspace"
          >
            <MessageSquare className="w-5 h-5" />
          </button>
        )}

        {/* Sliders */}
        {!workspaceOpen && activeTab !== 'table' && (
          <div className="absolute left-6 top-1/2 -translate-y-1/2 h-[40vh] z-40 flex gap-3 bg-white/5 backdrop-blur-md p-2 rounded-2xl border border-white/5 shadow-sm">
            <div className="flex flex-col items-center gap-2 h-full">
              <label htmlFor="panY-slider" className="sr-only">Vertical Pan Navigation</label>
              <input
                id="panY-slider"
                type="range" min="0" max="100" value={panY}
                onChange={e => setPanY(Number(e.target.value))}
                title="Pan Y"
                aria-label="Vertical Pan Slider"
                className="h-full appearance-none bg-white/10 rounded-full w-1 outline-none slider-vertical"
              />
            </div>
          </div>
        )}

        {/* Node Toolbar */}
        {selectedNode && (
          <div className={`absolute left-1/2 -translate-x-1/2 z-50 transition-all duration-500 ${workspaceOpen ? 'bottom-6' : 'bottom-10'}`}>
            <div className="bg-slate-900 border border-white/10 rounded-2xl p-4 shadow-xl w-80 backdrop-blur-xl">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-bold text-white text-sm truncate">{selectedNode.label}</h3>
                <span className="text-[10px] font-mono text-emerald-400">Z{selectedNode.z}</span>
              </div>
              <p className="text-[11px] text-slate-400 line-clamp-1 mb-3">{selectedNode.description}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowLauncher(true)}
                  className="flex-1 bg-emerald-600 text-white text-[10px] font-bold py-2 px-3 rounded-lg flex items-center justify-center gap-2 hover:bg-emerald-500 transition-colors"
                >
                  <Bot className="w-3.5 h-3.5" />
                  ACTIVATE AGENT
                </button>
                <button
                  onClick={() => setSelectedNode(null)}
                  title="Close node details"
                  aria-label="Close details"
                  className="p-2 bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Notification */}
        {notification && (
          <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] px-4 py-2 rounded-full shadow-2xl z-[60] border border-emerald-500/30 flex items-center gap-2 animate-in fade-in zoom-in slide-in-from-top-2">
            <Sparkles className="w-3 h-3 text-emerald-400" />
            {notification}
          </div>
        )}

        {/* Terminal Toggle */}
        <button
          onClick={() => setTerminalOpen(!terminalOpen)}
          title="Toggle Swarm Terminal"
          aria-label="Toggle Swarm Stream Terminal"
          className={`fixed left-6 bottom-6 z-[60] p-3 rounded-full transition-all ${terminalOpen ? 'bg-emerald-500 text-slate-950' : 'bg-slate-900 text-slate-400 border border-white/5'}`}
        >
          <Terminal className="w-5 h-5" />
        </button>

        {/* Mini Swarm Terminal Popover */}
        {terminalOpen && (
          <div className="fixed left-6 bottom-20 w-72 h-64 bg-slate-950 border border-white/10 rounded-2xl shadow-2xl z-[60] flex flex-col overflow-hidden animate-in slide-in-from-bottom-4">
            <div className="px-3 py-2 border-b border-white/5 flex justify-between items-center bg-slate-900">
              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Swarm Stream</span>
              <div className={`w-1.5 h-1.5 rounded-full ${swarmConnected ? 'bg-emerald-500' : 'bg-red-500'}`} />
            </div>
            <div ref={terminalRef} className="flex-1 p-3 overflow-y-auto font-mono text-[9px] space-y-2 no-scrollbar">
              {events.map(ev => <EventRow key={ev.id} ev={ev} />)}
            </div>
          </div>
        )}
      </div>

      {/* ── RIGHT ZONE: AGENT WORKSPACE ── */}
      {workspaceOpen && (
        <AgentWorkspace
          sessionId={activeSessionId}
          onClose={() => setWorkspaceOpen(false)}
        />
      )}

      {/* ── MODALS ── */}
      {showLauncher && selectedNode && (
        <SessionLauncher
          node={selectedNode}
          onClose={() => setShowLauncher(false)}
          onCreated={handleSessionCreated}
        />
      )}
    </div>
  );
}

export default App;
