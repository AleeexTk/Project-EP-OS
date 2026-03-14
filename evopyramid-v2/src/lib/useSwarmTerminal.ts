import { useCallback, useEffect, useRef, useState } from 'react';
import { SWARM_WS_URL } from './config';

export type SwarmEventType =
  | 'session.created'
  | 'session.message'
  | 'session.status_changed'
  | 'status.response'
  | 'system';

export interface SwarmEvent {
  id: string;
  ts: string;
  event: SwarmEventType;
  provider?: string;
  node_id?: string;
  node_z?: number;
  session_id?: string;
  task_title?: string;
  status?: string;
  new_status?: string;
  role?: string;
  content?: string;
  external_url?: string;
  raw?: Record<string, unknown>;
}

const makeSystemEvent = (content: string): SwarmEvent => ({
  id: crypto.randomUUID(),
  ts: new Date().toISOString(),
  event: 'system',
  content,
});

export function useSwarmTerminal() {
  const [events, setEvents] = useState<SwarmEvent[]>([makeSystemEvent('Connecting to Session Registry...')]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retryTimerRef = useRef<number | null>(null);

  const pushEvent = useCallback((event: SwarmEvent) => {
    setEvents((prev) => [...prev.slice(-199), event]);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const connect = () => {
      if (cancelled) {
        return;
      }
      const ws = new WebSocket(SWARM_WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (cancelled) {
          ws.close();
          return;
        }
        setConnected(true);
        pushEvent(makeSystemEvent('Swarm terminal connected'));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          pushEvent({
            id: crypto.randomUUID(),
            ts: new Date().toISOString(),
            event: data.event ?? 'system',
            ...data,
            raw: data,
          });
        } catch {
          pushEvent(makeSystemEvent(`Raw: ${event.data}`));
        }
      };

      ws.onclose = () => {
        if (cancelled) {
          return;
        }
        setConnected(false);
        pushEvent(makeSystemEvent('Connection lost. Retrying in 4s...'));
        retryTimerRef.current = window.setTimeout(connect, 4000);
      };

      ws.onerror = () => ws.close();
    };

    connect();

    return () => {
      cancelled = true;
      if (retryTimerRef.current !== null) {
        clearTimeout(retryTimerRef.current);
      }
      wsRef.current?.close();
    };
  }, [pushEvent]);

  const sendCommand = useCallback((command: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(command));
    }
  }, []);

  const queryStatus = useCallback(() => {
    sendCommand({ cmd: 'status' });
  }, [sendCommand]);

  return { events, connected, sendCommand, queryStatus };
}
