import { useCallback, useState } from 'react';
import { SESSION_API_BASE } from './config';

export type Provider = 'gpt' | 'gemini' | 'claude' | 'copilot' | 'ollama';
export type SessionStatus = 'pending' | 'active' | 'waiting' | 'review' | 'done' | 'paused' | 'conflict';

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
  external_url?: string;
}

export interface ProviderInfo {
  name: string;
  base_chat_url: string;
  has_api: boolean;
  color_primary: string;
  color_secondary?: string;
  visual_marker: string;
}

export function useSessionRegistry() {
  const [sessions, setSessions] = useState<AgentSession[]>([]);
  const [providers, setProviders] = useState<Record<Provider, ProviderInfo>>({} as Record<Provider, ProviderInfo>);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiCall = useCallback(async <T,>(path: string, options?: RequestInit): Promise<T | null> => {
    setError(null);
    try {
      const response = await fetch(`${SESSION_API_BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      if (!response.ok) {
        const message = await response.text();
        throw new Error(`${response.status}: ${message}`);
      }
      return (await response.json()) as T;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown API error');
      return null;
    }
  }, []);

  const loadSessions = useCallback(
    async (nodeId?: string) => {
      setLoading(true);
      const query = nodeId ? `?node_id=${encodeURIComponent(nodeId)}` : '';
      const data = await apiCall<AgentSession[]>(`/sessions${query}`);
      if (data) {
        setSessions(data);
      }
      setLoading(false);
    },
    [apiCall],
  );

  const createSession = useCallback(
    async (payload: SessionCreatePayload): Promise<AgentSession | null> => {
      setLoading(true);
      const data = await apiCall<AgentSession>('/sessions', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      if (data) {
        setSessions((prev) => [data, ...prev]);
      }
      setLoading(false);
      return data;
    },
    [apiCall],
  );

  const addMessage = useCallback(
    async (
      sessionId: string,
      content: string,
      role: 'user' | 'assistant' = 'user',
      triggerAI = false,
    ): Promise<AgentSession | null> => {
      const query = triggerAI ? '?ai=true' : '';
      const data = await apiCall<AgentSession>(`/sessions/${sessionId}/messages${query}`, {
        method: 'POST',
        body: JSON.stringify({ role, content }),
      });
      if (data) {
        setSessions((prev) => prev.map((session) => (session.id === sessionId ? data : session)));
      }
      return data;
    },
    [apiCall],
  );

  const updateStatus = useCallback(
    async (sessionId: string, status: SessionStatus): Promise<AgentSession | null> => {
      const data = await apiCall<AgentSession>(`/sessions/${sessionId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      });
      if (data) {
        setSessions((prev) => prev.map((session) => (session.id === sessionId ? data : session)));
      }
      return data;
    },
    [apiCall],
  );

  const deleteSession = useCallback(
    async (sessionId: string) => {
      await apiCall(`/sessions/${sessionId}`, { method: 'DELETE' });
      setSessions((prev) => prev.filter((session) => session.id !== sessionId));
    },
    [apiCall],
  );

  const loadProviders = useCallback(async () => {
    const data = await apiCall<Record<Provider, ProviderInfo>>('/providers');
    if (data) {
      setProviders(data);
    }
  }, [apiCall]);

  const openInBrowser = useCallback(
    async (provider: Provider, taskTitle?: string, nodeId?: string, existingUrl?: string) => {
      const directUrl = (existingUrl ?? '').trim();
      if (directUrl) {
        const electronApi = (window as any).electronAPI;
        if (electronApi?.openAgent) {
          electronApi.openAgent(directUrl);
        } else {
          window.open(directUrl, '_blank', 'noopener,noreferrer');
        }
        return;
      }

      const params = new URLSearchParams();
      if (taskTitle) {
        params.set('task_title', taskTitle);
      }
      if (nodeId) {
        params.set('node_id', nodeId);
      }
      const data = await apiCall<{ url: string }>(`/providers/${provider}/url?${params.toString()}`);
      if (data?.url) {
        const electronApi = (window as any).electronAPI;
        if (electronApi?.openAgent) {
          electronApi.openAgent(data.url);
        } else {
          window.open(data.url, '_blank', 'noopener,noreferrer');
        }
      }
    },
    [apiCall],
  );

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


