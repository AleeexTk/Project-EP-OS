import { useEffect, useRef, useState } from 'react';
import { CORE_WS_URL } from './config';
import { CENTER, EvoNode, NodeKind, NodeStatus, Sector, generateEmptyGridNodes, getRadius } from './evo';

const STATUS_MAP: Record<string, NodeStatus> = {
  active: 'active',
  idle: 'idle',
  degraded: 'degraded',
  warning: 'warning',
  failed: 'failed',
  quarantined: 'quarantined',
  error: 'failed',
  none: 'none',
};

const KIND_MAP: Record<string, NodeKind> = {
  module: 'module',
  service: 'service',
  agent: 'agent',
  memory: 'memory',
  protocol: 'protocol',
  canon: 'canon',
  runtime: 'runtime',
  empty: 'empty',
};

const SECTOR_MAP: Record<string, Sector> = {
  spine: 'spine',
  purple: 'purple',
  red: 'red',
  gold: 'gold',
  green: 'green',
  empty: 'empty',
};

const normalizeStatus = (status: unknown): NodeStatus => {
  const key = String(status ?? 'idle').toLowerCase();
  return STATUS_MAP[key] ?? 'idle';
};

const normalizeKind = (kind: unknown): NodeKind => {
  const key = String(kind ?? 'module').toLowerCase();
  return KIND_MAP[key] ?? 'module';
};

const normalizeSector = (sector: unknown): Sector => {
  const key = String(sector ?? 'spine').toLowerCase();
  return SECTOR_MAP[key] ?? 'spine';
};

const normalizeLinks = (links: unknown): string[] => {
  if (!Array.isArray(links)) {
    return [];
  }
  return links.map((link) => String(link)).filter((link) => link.length > 0);
};

const clampInt = (value: number, min: number, max: number): number => {
  if (!Number.isFinite(value)) {
    return min;
  }
  return Math.max(min, Math.min(max, Math.round(value)));
};

const normalizeCoords = (rawX: unknown, rawY: unknown, rawZ: unknown) => {
  const z = clampInt(Number(rawZ ?? 1), 1, 17);
  const radius = getRadius(z);
  const min = CENTER - radius;
  const max = CENTER + radius;
  const x = clampInt(Number(rawX ?? CENTER), min, max);
  const y = clampInt(Number(rawY ?? CENTER), min, max);
  return { x, y, z };
};

const resolveLayer = (value: any, z: number): EvoNode['layer'] => {
  const layerType = String(value?.layer_type ?? '').toLowerCase();
  if (layerType === 'alpha' || layerType === 'beta' || layerType === 'gamma') {
    return layerType;
  }
  if (z >= 11) {
    return 'alpha';
  }
  if (z >= 5) {
    return 'beta';
  }
  return 'gamma';
};

const toNode = (id: string, value: any): EvoNode => {
  const coords = normalizeCoords(value?.coords?.x, value?.coords?.y, value?.z_level ?? value?.coords?.z);
  const metadata = value?.metadata && typeof value.metadata === 'object' && !Array.isArray(value.metadata)
    ? (value.metadata as Record<string, unknown>)
    : undefined;

  return {
    id,
    x: coords.x,
    y: coords.y,
    z: coords.z,
    sector: normalizeSector(value?.sector),
    type: coords.z % 2 === 0 ? 'link' : 'structural',
    status: normalizeStatus(value?.state),
    layer: resolveLayer(value, coords.z),
    kind: normalizeKind(value?.kind),
    label: value?.title ?? id,
    description: value?.summary ?? '',
    links: normalizeLinks(value?.links),
    capability: value?.capability,
    metadata,
    runtime_canon_flag: value?.runtime_canon_flag,
  };
};

const coordKey = (node: { z: number; x: number; y: number }) => `${node.z}:${node.x}:${node.y}`;

const buildNodesFromBackend = (backendNodes: Record<string, any>, prevNodes: EvoNode[]): EvoNode[] => {
  const nextNodes = generateEmptyGridNodes();
  const indexByCoord = new Map<string, number>();
  const prevById = new Map(prevNodes.map((node) => [node.id, node]));

  nextNodes.forEach((node, index) => {
    indexByCoord.set(coordKey(node), index);
  });

  Object.entries(backendNodes).forEach(([id, raw]) => {
    const mapped = toNode(id, raw);
    const prev = prevById.get(mapped.id);
    const merged = prev?.activeAgents ? { ...mapped, activeAgents: prev.activeAgents } : mapped;

    const index = indexByCoord.get(coordKey(merged));
    if (index !== undefined) {
      nextNodes[index] = { ...nextNodes[index], ...merged };
      return;
    }

    nextNodes.push(merged);
  });

  return nextNodes;
};

export function usePyramidState() {
  const [nodes, setNodes] = useState<EvoNode[]>(generateEmptyGridNodes());
  const [isConnected, setIsConnected] = useState(false);
  const backendNodesRef = useRef<Record<string, any>>({});

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let cancelled = false;

    const applySnapshot = (snapshot: Record<string, any>) => {
      backendNodesRef.current = snapshot;
      setNodes((prevNodes) => buildNodesFromBackend(snapshot, prevNodes));
    };

    const connect = () => {
      if (cancelled) {
        return;
      }
      socket = new WebSocket(CORE_WS_URL);

      socket.onopen = () => {
        if (cancelled) {
          socket?.close();
          return;
        }
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'full_state') {
            const snapshot = message?.data?.nodes;
            if (snapshot && typeof snapshot === 'object') {
              applySnapshot(snapshot as Record<string, any>);
            }
          } else if (message.type === 'node_update' && message?.data?.id) {
            const nextSnapshot = {
              ...backendNodesRef.current,
              [message.data.id]: message.data,
            };
            applySnapshot(nextSnapshot);
          }
        } catch {
          // Keep current visual state if payload is malformed.
        }
      };

      socket.onclose = () => {
        if (cancelled) {
          return;
        }
        setIsConnected(false);
        reconnectTimer = window.setTimeout(connect, 3000);
      };

      socket.onerror = () => {
        socket?.close();
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (reconnectTimer !== null) {
        clearTimeout(reconnectTimer);
      }
      socket?.close();
    };
  }, []);

  return { nodes, isConnected };
}


