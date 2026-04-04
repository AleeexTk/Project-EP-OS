
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
  coherence?: number;    // TRINITY RESONANCE v3.0 logic (0.0 to 1.0)
  trinity_state?: string; // FSM State (LISTENING, PARSING, etc.)
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
  // Size = 18 - Z. Radius is half of that.
  return (18 - z) / 2;
}

export function isValidPosition(x: number, y: number, z: number): boolean {
  const size = 18 - z;
  const start = CENTER - Math.floor(size / 2);
  const end = start + size - 1;
  return x >= start && x <= end && y >= start && y <= end;
}

export const SECTOR_COLORS: Record<Sector, string> = {
  spine: '#ffffff', // Nuclei (White)
  purple: '#7c3aed', // Soul (Reflective)
  red: '#7f1d1d',    // Provocateur (Stability - Deep Red)
  gold: '#d97706',   // Synthesis (Integration)
  green: '#15803d',  // Trailblazer (Efficiency)
  empty: '#1e293b',  // Dark slate for background/empty
};

export function getGradientColor(node: EvoNode): string {
  // Rule: Central Cross (Spine) is always White
  if (node.x === CENTER || node.y === CENTER) return '#ffffff';
  
  // Rule: Odd levels (Nuclei) are always White
  if (node.z % 2 !== 0) return '#ffffff';
  
  // Quadrant detection for Even levels
  const isNorth = node.y < CENTER;
  const isWest = node.x < CENTER;
  
  let baseColor = SECTOR_COLORS.green; // NW
  if (isNorth && !isWest) baseColor = SECTOR_COLORS.red;    // NE
  if (!isNorth && isWest) baseColor = SECTOR_COLORS.gold;   // SW
  if (!isNorth && !isWest) baseColor = SECTOR_COLORS.purple; // SE

  // Gradient based on distance from center
  const dist = Math.sqrt(Math.pow(node.x - CENTER, 2) + Math.pow(node.y - CENTER, 2));
  const maxDist = getRadius(node.z) * Math.sqrt(2);
  const factor = maxDist > 0 ? 1 - (dist / (maxDist * 1.2)) : 1;
  
  // Apply intensity (simple hex darkening/lightening simulation)
  return baseColor; // Placeholder for real hex-shift logic, will refine in EvoPyramid.tsx
}

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



