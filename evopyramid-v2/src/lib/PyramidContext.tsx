import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import { CORE_WS_URL } from './config';
import { EvoNode, NodeStatus, NodeKind, Sector, generateEmptyGridNodes, getRadius, CENTER } from './evo';

// --- Maps and Normalizers (Moved from usePyramidState for centralization) ---
const STATUS_MAP: Record<string, NodeStatus> = {
  active: 'active', idle: 'idle', degraded: 'degraded', warning: 'warning',
  failed: 'failed', quarantined: 'quarantined', error: 'failed', none: 'none',
};

const KIND_MAP: Record<string, NodeKind> = {
  module: 'module', service: 'service', agent: 'agent', memory: 'memory',
  protocol: 'protocol', canon: 'canon', runtime: 'runtime', empty: 'empty',
};

const SECTOR_MAP: Record<string, Sector> = {
  spine: 'spine', purple: 'purple', red: 'red', gold: 'gold', green: 'green', empty: 'empty',
};

const normalizeStatus = (status: unknown): NodeStatus => STATUS_MAP[String(status ?? 'idle').toLowerCase()] ?? 'idle';
const normalizeKind = (kind: unknown): NodeKind => KIND_MAP[String(kind ?? 'module').toLowerCase()] ?? 'module';
const normalizeSector = (sector: unknown): Sector => SECTOR_MAP[String(sector ?? 'spine').toLowerCase()] ?? 'spine';

const normalizeLinks = (links: unknown): string[] => 
  Array.isArray(links) ? links.map(String).filter(l => l.length > 0) : [];

const clampInt = (value: number, min: number, max: number): number => 
  !Number.isFinite(value) ? min : Math.max(min, Math.min(max, Math.round(value)));

const normalizeCoords = (rawX: unknown, rawY: unknown, rawZ: unknown) => {
  const z = clampInt(Number(rawZ ?? 1), 1, 17);
  const radius = getRadius(z);
  const min = CENTER - radius;
  const max = CENTER + radius;
  return { x: clampInt(Number(rawX ?? CENTER), min, max), y: clampInt(Number(rawY ?? CENTER), min, max), z };
};

const resolveLayer = (value: any, z: number): EvoNode['layer'] => {
  const layerType = String(value?.layer_type ?? '').toLowerCase();
  if (['alpha', 'beta', 'gamma'].includes(layerType)) return layerType as any;
  return z >= 11 ? 'alpha' : z >= 5 ? 'beta' : 'gamma';
};

const toNode = (id: string, value: any): EvoNode => {
  const coords = normalizeCoords(value?.coords?.x, value?.coords?.y, value?.z_level ?? value?.coords?.z);
  return {
    id, x: coords.x, y: coords.y, z: coords.z,
    sector: normalizeSector(value?.sector),
    type: coords.z % 2 === 0 ? 'link' : 'structural',
    status: normalizeStatus(value?.state),
    layer: resolveLayer(value, coords.z),
    kind: normalizeKind(value?.kind),
    label: value?.title ?? id,
    description: value?.summary ?? '',
    links: normalizeLinks(value?.links),
    capability: value?.capability,
    metadata: value?.metadata && typeof value.metadata === 'object' ? value.metadata : undefined,
    runtime_canon_flag: value?.runtime_canon_flag,
  };
};

const coordKey = (node: { z: number; x: number; y: number }) => `${node.z}:${node.x}:${node.y}`;
const EMPTY_GRID_CACHE = generateEmptyGridNodes();
const EMPTY_GRID_INDEX = new Map(EMPTY_GRID_CACHE.map((node, i) => [coordKey(node), i]));

const buildNodesFromBackend = (backendNodes: Record<string, any>, prevNodes: EvoNode[]): EvoNode[] => {
  const nextNodes = EMPTY_GRID_CACHE.map(node => ({ ...node }));
  const prevById = new Map(prevNodes.map(node => [node.id, node]));

  Object.entries(backendNodes).forEach(([id, raw]) => {
    const mapped = toNode(id, raw);
    const prev = prevById.get(mapped.id);
    const merged = prev?.activeAgents ? { ...mapped, activeAgents: prev.activeAgents } : mapped;
    const index = EMPTY_GRID_INDEX.get(coordKey(merged));
    if (index !== undefined) nextNodes[index] = { ...nextNodes[index], ...merged };
    else nextNodes.push(merged);
  });
  return nextNodes;
};

// --- Context Definition ---
interface PyramidStateContextType {
  nodes: EvoNode[];
  isConnected: boolean;
  latestZBusEvent: any;
  systemMetrics: any;
}

const PyramidContext = createContext<PyramidStateContextType | undefined>(undefined);

export function PyramidProvider({ children }: { children: ReactNode }) {
  const [nodes, setNodes] = useState<EvoNode[]>(EMPTY_GRID_CACHE);
  const [isConnected, setIsConnected] = useState(false);
  const [latestZBusEvent, setLatestZBusEvent] = useState<any>(null);
  const [systemMetrics, setSystemMetrics] = useState<any>(null);
  const backendNodesRef = useRef<Record<string, any>>({});

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let cancelled = false;

    const applySnapshot = (snapshot: Record<string, any>) => {
      backendNodesRef.current = snapshot;
      setNodes(prev => buildNodesFromBackend(snapshot, prev));
    };

    const connect = () => {
      if (cancelled) return;
      socket = new WebSocket(CORE_WS_URL);
      
      socket.onopen = () => {
        if (!cancelled) setIsConnected(true);
        else socket?.close();
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'full_state') {
            if (message?.data?.nodes) applySnapshot(message.data.nodes);
            if (message?.data?.system_metrics) setSystemMetrics(message.data.system_metrics);
          } else if (message.type === 'node_update' && message?.data?.id) {
            const nextSnapshot = { ...backendNodesRef.current, [message.data.id]: message.data };
            applySnapshot(nextSnapshot);
          } else if (message.type === 'system_metrics_update') {
            setSystemMetrics(message.data);
          } else if (message.type === 'zbus_event') {
            setLatestZBusEvent(message.data);
          }
        } catch (e) { console.error('WS Parse Error', e); }
      };

      socket.onclose = () => {
        if (!cancelled) {
          setIsConnected(false);
          reconnectTimer = window.setTimeout(connect, 3000);
        }
      };

      socket.onerror = () => socket?.close();
    };

    connect();
    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  return (
    <PyramidContext.Provider value={{ nodes, isConnected, latestZBusEvent, systemMetrics }}>
      {children}
    </PyramidContext.Provider>
  );
}

export function usePyramidContext() {
  const context = useContext(PyramidContext);
  if (context === undefined) {
    throw new Error('usePyramidContext must be used within a PyramidProvider');
  }
  return context;
}
