
export type Sector = 'spine' | 'purple' | 'red' | 'gold' | 'green' | 'empty';
export type NodeStatus = 'active' | 'idle' | 'degraded' | 'failed' | 'quarantined' | 'none' | 'warning';
export type Layer = 'alpha' | 'beta' | 'gamma' | 'pear' | 'z17' | 'structure';
export type NodeKind = 'module' | 'service' | 'agent' | 'memory' | 'protocol' | 'canon' | 'runtime' | 'empty';

export interface AgentActivity {
  id: string;
  model: string;
  color: string;
  task: string;
}

export interface EvoNode {
  id: string;
  x: number;
  y: number;
  z: number;
  sector: Sector;
  type: 'structural' | 'link';
  status: NodeStatus;
  layer: Layer;
  kind: NodeKind;
  label: string;
  description?: string;
  agentRole?: string;
  capability?: string;
  links: string[];
  activeAgents?: AgentActivity[];
  metadata?: Record<string, unknown>;
  runtime_canon_flag?: 'canon' | 'runtime' | 'degraded' | 'quarantined';
}

// --- ZBus Event Schemas ---

export interface NodeStartEvent {
  event_type: "NODE_START";
  node_id: string;
  task_id: string;
  trace_id: string;
  provider?: string;
  status: "running";
  simulation: boolean;
  timestamp: string;
  payload: Record<string, any>;
}

export interface ProviderSelectedEvent {
  event_type: "PROVIDER_SELECTED";
  node_id: string;
  task_id: string;
  trace_id: string;
  provider: string;
  status: "running";
  simulation: boolean;
  timestamp: string;
  payload: Record<string, any>;
}

export interface ProviderTimeoutEvent {
  event_type: "PROVIDER_TIMEOUT";
  node_id: string;
  task_id: string;
  trace_id: string;
  provider: string;
  status: "degraded";
  simulation: boolean;
  timestamp: string;
  payload: Record<string, any>;
}

export interface NodeFallbackInitEvent {
  event_type: "NODE_FALLBACK_INIT";
  node_id: string;
  task_id: string;
  trace_id: string;
  provider: string;
  fallback_to: string;
  status: "degraded";
  simulation: boolean;
  timestamp: string;
  payload: Record<string, any>;
}

export interface NodeRecoverySuccessEvent {
  event_type: "NODE_RECOVERY_SUCCESS";
  node_id: string;
  task_id: string;
  trace_id: string;
  provider: string;
  status: "healthy";
  simulation: boolean;
  timestamp: string;
  payload: Record<string, any>;
}

export interface NodeFailureEvent {
  event_type: "NODE_FAILURE";
  node_id: string;
  task_id: string;
  trace_id: string;
  provider: string;
  status: "failed";
  simulation: boolean;
  timestamp: string;
  payload: Record<string, any>;
}

export type ZBusNodeEvent =
  | NodeStartEvent
  | ProviderSelectedEvent
  | ProviderTimeoutEvent
  | NodeFallbackInitEvent
  | NodeRecoverySuccessEvent
  | NodeFailureEvent;


export const GRID_SIZE = 17;
export const CENTER = 9; // 1-based index, so 9 is the center of 17

export function getRadius(z: number): number {
  // Z is 1-based (1 to 17)
  if (z % 2 !== 0) {
    // Odd (Structural)
    return (17 - z) / 2;
  } else {
    // Even (Link) - inherits from Z+1
    return (17 - (z + 1)) / 2;
  }
}

export function isValidPosition(x: number, y: number, z: number): boolean {
  const r = getRadius(z);
  return Math.abs(x - CENTER) <= r && Math.abs(y - CENTER) <= r;
}

export const SECTOR_COLORS: Record<Sector, string> = {
  spine: '#1f2937', // gray-800 (Dark for light background)
  purple: '#a855f7', // purple-500
  red: '#ef4444',    // red-500
  gold: '#eab308',   // yellow-500
  green: '#22c55e',  // green-500
  empty: '#e5e7eb',  // gray-200 (Light gray for empty slots)
};

export const STATUS_COLORS: Record<NodeStatus, string> = {
  active: '#22c55e',
  idle: '#94a3b8',
  degraded: '#f59e0b',
  warning: '#f97316',
  failed: '#ef4444',
  quarantined: '#a855f7',
  none: '#d1d5db',
};

export function generateEmptyGridNodes(): EvoNode[] {
  const nodes: EvoNode[] = [];

  for (let z = 1; z <= 17; z++) {
    const r = getRadius(z);
    const isStructural = z % 2 !== 0;

    for (let x = CENTER - r; x <= CENTER + r; x++) {
      for (let y = CENTER - r; y <= CENTER + r; y++) {
        nodes.push({
          id: `${z}-${x}-${y}`,
          x,
          y,
          z,
          sector: 'empty',
          type: isStructural ? 'structural' : 'link',
          status: 'none',
          layer: 'structure',
          kind: 'empty',
          label: 'Empty Slot',
          links: [],
          description: 'Available for allocation',
        });
      }
    }
  }

  return nodes;
}
export function generateMockNodes(): EvoNode[] {
  const nodesMap = new Map<string, EvoNode>();

  // Helper to add node
  const addNode = (z: number, x: number, y: number, sector: Sector, id: string, label: string, layer: Layer, kind: NodeKind, status: NodeStatus = 'active', links: string[] = [], extra: Partial<EvoNode> = {}) => {
    const isStructural = z % 2 !== 0;
    const key = `${z}-${x}-${y}`;
    nodesMap.set(key, {
      id,
      x,
      y,
      z,
      sector,
      type: isStructural ? 'structural' : 'link',
      status,
      layer,
      kind,
      label,
      links,
      ...extra
    });
  };

  // --- Z17: Apex (Phase A) ---
  addNode(17, 9, 9, 'spine', 'apex_core', 'Apex Core', 'z17', 'canon', 'active', ['spine_router'], { 
    capability: 'apex_core/manifest.json', 
    description: 'Canon Registry. The Source of Truth.',
    activeAgents: [{ id: 'a1', model: 'Claude-3.5-Sonnet', color: '#d97757', task: 'Validating Canon integrity' }]
  });

  // --- Z16: Link ---
  addNode(16, 9, 9, 'spine', 'spine_router', 'Spine Router', 'z17', 'protocol', 'active', ['atlas_generator', 'pear_seed', 'z15_spine'], { description: 'Routing between Z17 and Z15' });

  // --- Z15: Atlas (Phase A) ---
  addNode(15, 8, 9, 'purple', 'atlas_generator', 'Atlas Generator', 'alpha', 'service', 'active', [], { capability: 'atlas_generator/manifest.json', description: 'Generates system topology map' });
  addNode(15, 9, 9, 'spine', 'z15_spine', 'Z15 Spine', 'alpha', 'module', 'active', ['memory_core', 'canon_rules']);

  // --- Z13: Alpha / Intent (Phase B) ---
  addNode(13, 9, 9, 'spine', 'pear_seed', 'PEAR Seed', 'alpha', 'protocol', 'active', ['beta_nexus'], { capability: 'protocol_manifest.yaml', description: 'Intent System. Input Impulse.' });
  addNode(13, 7, 9, 'purple', 'memory_core', 'Memory Core', 'alpha', 'memory', 'active', [], { capability: 'hybrid_agi/memory.py', description: 'Long-term memory primitives' });
  addNode(13, 11, 9, 'gold', 'canon_rules', 'Canon Rules', 'alpha', 'canon', 'idle', [], { capability: 'canon_builder/validators/', description: 'Automatic canon compliance checks' });

  // --- Z9: Beta / Agents (PEAR Containers) (Phase B) ---
  addNode(9, 9, 9, 'spine', 'beta_nexus', 'Beta Nexus', 'beta', 'runtime', 'active', ['agent_trailblazer', 'agent_provocateur', 'agent_soul', 'agent_prometheus']);
  addNode(9, 8, 8, 'green', 'agent_trailblazer', 'Trailblazer', 'pear', 'agent', 'active', ['chaos_engine'], { agentRole: 'Ollama/Local', description: 'PEAR Container #1: Scout' });
  addNode(9, 10, 8, 'green', 'agent_provocateur', 'Provocateur', 'pear', 'agent', 'active', ['chaos_engine'], { agentRole: 'GPT/Critic', description: 'PEAR Container #2: Critic' });
  addNode(9, 8, 10, 'green', 'agent_soul', 'Soul', 'pear', 'agent', 'active', ['chaos_engine'], { agentRole: 'Local/Core', description: 'PEAR Container #3: Meaning' });
  addNode(9, 10, 10, 'green', 'agent_prometheus', 'Prometheus', 'pear', 'agent', 'active', ['chaos_engine'], { agentRole: 'Gemini/Synth', description: 'PEAR Container #4: Synthesizer' });

  // --- Z7: Orchestration / Interface (Phase B) ---
  addNode(7, 9, 9, 'spine', 'orchestrator', 'Orchestrator', 'beta', 'service', 'active', ['api_gateway', 'gamma_spine'], { 
    capability: 'orchestrator.py', 
    description: 'Global Nexus Orchestration',
    activeAgents: [{ id: 'a2', model: 'GPT-4o', color: '#10a37f', task: 'Resolving routing conflict' }]
  });
  addNode(7, 9, 7, 'red', 'api_gateway', 'API Gateway', 'beta', 'protocol', 'active', [], { capability: 'api_gateway.py', description: 'FastAPI routing (alpha, beta, gamma)' });
  addNode(7, 7, 9, 'green', 'chaos_engine', 'Chaos Engine', 'beta', 'runtime', 'warning', ['orchestrator'], { 
    description: 'Conflict Synthesis (PEAR Phase 4)',
    activeAgents: [
      { id: 'a3', model: 'Gemini-1.5-Pro', color: '#1a73e8', task: 'Synthesizing divergent outputs' },
      { id: 'a4', model: 'Llama-3-70B', color: '#043b72', task: 'Providing adversarial critique' }
    ]
  });
  addNode(7, 11, 9, 'purple', 'provider_matrix', 'Provider Matrix', 'beta', 'module', 'active', ['nexus_bridge'], { capability: 'provider_matrix.py', description: 'Configuration of available models' });

  // --- Z8: mvp_browser modules ---
  addNode(8, 8, 9, 'spine', 'spine_bridge', 'Spine Bridge', 'beta', 'protocol', 'active');
  addNode(8, 10, 9, 'green', 'semantic_engine', 'Semantic Engine', 'beta', 'service', 'active');
  addNode(8, 9, 9, 'purple', 'purple_sanctuary', 'Purple Sanctuary', 'beta', 'module', 'active');
  addNode(8, 9, 10, 'gold', 'view_matrix', 'View Matrix', 'beta', 'module', 'active');

  // --- Z5: Observer / Gamma (Phase C) ---
  addNode(5, 9, 9, 'spine', 'gamma_spine', 'Gamma Spine', 'gamma', 'module', 'active', ['tri_heartbeat', 'observer_core']);
  addNode(5, 8, 9, 'purple', 'observer_core', 'Observer Core', 'gamma', 'observer' as any, 'active', ['auto_merge'], { description: 'Validation & Coherence Monitoring' });
  addNode(5, 10, 9, 'purple', 'nexus_bridge', 'Nexus Bridge', 'beta', 'bridge' as any, 'degraded', [], { capability: 'nexus_bridge.py', description: 'Provider Routing (Graceful Fallback)' });

  // --- Z3: Sync / Hive (Phase C) ---
  addNode(3, 9, 9, 'spine', 'tri_heartbeat', 'Tri-Heartbeat', 'gamma', 'service', 'active', ['joint_sync'], { capability: 'tri_heartbeat.py', description: 'Continuous 3-phase pulse' });
  addNode(3, 7, 7, 'gold', 'joint_sync', 'Joint Sync', 'gamma', 'protocol', 'active', ['root_anchor'], { capability: 'joint_sync.py', description: 'PEAR <-> Heartbeat Ritual' });
  addNode(3, 11, 11, 'gold', 'auto_merge', 'Auto Merge', 'gamma', 'service', 'idle', ['root_anchor'], { capability: 'auto_merge.py', description: 'Runtime to Canon merge logic (γ > β)' });

  // --- Z1: Foundation / Archive (Phase D) ---
  addNode(1, 9, 9, 'spine', 'root_anchor', 'Root Anchor', 'gamma', 'canon', 'active', ['ancient_archive']);
  addNode(1, 5, 5, 'gold', 'ancient_archive', 'Ancient Archive', 'gamma', 'memory', 'idle', [], { description: 'Legacy Assimilation Pipeline' });

  const allNodes = generateEmptyGridNodes();
  const indexByCoords = new Map<string, number>();

  allNodes.forEach((node, index) => {
    indexByCoords.set(`${node.z}-${node.x}-${node.y}`, index);
  });

  nodesMap.forEach((node, key) => {
    const index = indexByCoords.get(key);
    if (index !== undefined) {
      allNodes[index] = node;
      return;
    }
    allNodes.push(node);
  });

  return allNodes;
}

