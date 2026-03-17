
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
  memory_color?: string;
  gravity?: number;
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


