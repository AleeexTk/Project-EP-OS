/**
 * useSessionRegistry
 * ───────────────────
 * REST client for the Session Registry API (port 8001).
 * Provides React state + actions for managing agent sessions.
 */

import { useState, useCallback } from 'react';
import { SESSION_API_BASE } from './useSwarmTerminal';

// ─── Types (mirroring backend Pydantic models) ───────────────────────────────

export type Provider = 'gpt' | 'gemini' | 'claude' | 'copilot' | 'ollama';
export type SessionStatus =
    | 'pending' | 'active' | 'waiting' | 'review' | 'done' | 'paused' | 'conflict';

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    ts: string;
    agent_ref?: string;
}

export interface AgentSession {
    id: string;
    node_id: string;
    node_z: number;
    node_sector: string;
    provider: Provider;
    account_hint?: string;
    model_hint?: string;
    task_title: string;
    task_context?: string;
    status: SessionStatus;
    created_at: string;
    updated_at: string;
    messages: Message[];
    external_url?: string;
}

export interface SessionCreatePayload {
    node_id: string;
    node_z: number;
    node_sector?: string;
    provider: Provider;
    account_hint?: string;
    model_hint?: string;
    task_title: string;
    task_context?: string;
}

export interface ProviderInfo {
    name: string;
    base_chat_url: string;
    has_api: boolean;
    color_primary: string;
    color_secondary?: string;
    visual_marker: string;
}

// ─── Hook ────────────────────────────────────────────────────────────────────

export function useSessionRegistry() {
    const [sessions, setSessions] = useState<AgentSession[]>([]);
    const [providers, setProviders] = useState<Record<Provider, ProviderInfo>>({} as any);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const apiCall = useCallback(async <T>(
        path: string,
        options?: RequestInit
    ): Promise<T | null> => {
        setError(null);
        try {
            const res = await fetch(`${SESSION_API_BASE}${path}`, {
                headers: { 'Content-Type': 'application/json' },
                ...options,
            });
            if (!res.ok) {
                const msg = await res.text();
                throw new Error(`${res.status}: ${msg}`);
            }
            return res.json() as Promise<T>;
        } catch (e: any) {
            setError(e.message ?? 'Unknown error');
            return null;
        }
    }, []);

    // ── Sessions ──────────────────────────────────────────────────────────────

    const loadSessions = useCallback(async (nodeId?: string) => {
        setLoading(true);
        const url = nodeId ? `/sessions?node_id=${encodeURIComponent(nodeId)}` : '/sessions';
        const data = await apiCall<AgentSession[]>(url);
        if (data) setSessions(data);
        setLoading(false);
    }, [apiCall]);

    const createSession = useCallback(async (payload: SessionCreatePayload): Promise<AgentSession | null> => {
        setLoading(true);
        const data = await apiCall<AgentSession>('/sessions', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        if (data) {
            setSessions(prev => [data, ...prev]);
        }
        setLoading(false);
        return data;
    }, [apiCall]);

    const addMessage = useCallback(async (
        sessionId: string,
        content: string,
        role: 'user' | 'assistant' = 'user',
        triggerAI: boolean = false
    ): Promise<AgentSession | null> => {
        const query = triggerAI ? '?ai=true' : '';
        const data = await apiCall<AgentSession>(`/sessions/${sessionId}/messages${query}`, {
            method: 'POST',
            body: JSON.stringify({ role, content }),
        });
        if (data) {
            setSessions(prev => prev.map(s => s.id === sessionId ? data : s));
        }
        return data;
    }, [apiCall]);

    const updateStatus = useCallback(async (
        sessionId: string,
        status: SessionStatus
    ): Promise<AgentSession | null> => {
        const data = await apiCall<AgentSession>(`/sessions/${sessionId}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status }),
        });
        if (data) {
            setSessions(prev => prev.map(s => s.id === sessionId ? data : s));
        }
        return data;
    }, [apiCall]);

    const deleteSession = useCallback(async (sessionId: string) => {
        await apiCall(`/sessions/${sessionId}`, { method: 'DELETE' });
        setSessions(prev => prev.filter(s => s.id !== sessionId));
    }, [apiCall]);

    // ── Providers ─────────────────────────────────────────────────────────────

    const loadProviders = useCallback(async () => {
        const data = await apiCall<Record<Provider, ProviderInfo>>('/providers');
        if (data) setProviders(data);
    }, [apiCall]);

    /** Open external chat URL in new browser tab OR Electron Workspace */
    const openInBrowser = useCallback(async (
        provider: Provider,
        taskTitle?: string,
        nodeId?: string
    ) => {
        const params = new URLSearchParams();
        if (taskTitle) params.set('task_title', taskTitle);
        if (nodeId) params.set('node_id', nodeId);
        const data = await apiCall<{ url: string }>(
            `/providers/${provider}/url?${params.toString()}`
        );
        if (data?.url) {
            // Check for Electron Desktop Bridge
            const electronAPI = (window as any).electronAPI;
            if (electronAPI) {
                electronAPI.openAgent(data.url);
            } else {
                window.open(data.url, '_blank', 'noopener,noreferrer');
            }
        }
    }, [apiCall]);

    return {
        sessions,
        providers,
        loading,
        error,
        loadSessions,
        createSession,
        addMessage,
        updateStatus,
        deleteSession,
        loadProviders,
        openInBrowser,
    };
}
