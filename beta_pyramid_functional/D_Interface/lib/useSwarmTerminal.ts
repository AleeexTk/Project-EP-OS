/**
 * useSwarmTerminal
 * ─────────────────
 * Connects to Session Registry WebSocket (/ws/swarm) and
 * streams all session events to the Swarm Terminal panel.
 * Z9 · β-layer · GREEN sector
 */

import { useState, useEffect, useRef, useCallback } from 'react';

export const SESSION_API_BASE = 'http://127.0.0.1:8001';
export const SWARM_WS_URL = 'ws://127.0.0.1:8001/ws/swarm';

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
    // raw fallback
    raw?: Record<string, unknown>;
}

function makeSystemEvent(msg: string): SwarmEvent {
    return {
        id: crypto.randomUUID(),
        ts: new Date().toISOString(),
        event: 'system',
        content: msg,
    };
}

export function useSwarmTerminal() {
    const [events, setEvents] = useState<SwarmEvent[]>([
        makeSystemEvent('Session Registry connecting…'),
    ]);
    const [connected, setConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const retryRef = useRef<number | undefined>(undefined);

    const pushEvent = useCallback((ev: SwarmEvent) => {
        setEvents(prev => [...prev.slice(-199), ev]); // keep last 200
    }, []);

    useEffect(() => {
        let cancelled = false;

        const connect = () => {
            if (cancelled) return;
            const ws = new WebSocket(SWARM_WS_URL);
            wsRef.current = ws;

            ws.onopen = () => {
                if (cancelled) { ws.close(); return; }
                setConnected(true);
                pushEvent(makeSystemEvent('✔ Swarm Terminal connected — Session Registry Z9 online'));
            };

            ws.onmessage = (e) => {
                try {
                    const data = JSON.parse(e.data);
                    const ev: SwarmEvent = {
                        id: crypto.randomUUID(),
                        ts: new Date().toISOString(),
                        event: data.event ?? 'system',
                        ...data,
                        raw: data,
                    };
                    pushEvent(ev);
                } catch {
                    pushEvent(makeSystemEvent(`Raw: ${e.data}`));
                }
            };

            ws.onclose = () => {
                if (cancelled) return;
                setConnected(false);
                pushEvent(makeSystemEvent('⚠ Connection lost. Retrying in 4s…'));
                retryRef.current = window.setTimeout(connect, 4000);
            };

            ws.onerror = () => {
                ws.close();
            };
        };

        connect();

        return () => {
            cancelled = true;
            clearTimeout(retryRef.current);
            wsRef.current?.close();
        };
    }, [pushEvent]);

    /** Send a command to the backend through the WS */
    const sendCommand = useCallback((cmd: Record<string, unknown>) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(cmd));
        }
    }, []);

    /** Ask registry for active session count */
    const queryStatus = useCallback(() => {
        sendCommand({ cmd: 'status' });
    }, [sendCommand]);

    return { events, connected, sendCommand, queryStatus };
}
