import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Bot, ExternalLink, PauseCircle, PlayCircle, Send, Terminal, Trash2, User, X, Zap } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';
import { AgentSession, SessionStatus, useSessionRegistry } from '../lib/useSessionRegistry';

interface AgentWorkspaceProps {
  sessionId: string | null;
  onClose: () => void;
  onSessionChange?: (sessionId: string) => void;
}

const STATUS_STYLE: Record<AgentSession['status'], string> = {
  pending: 'bg-slate-500/20 text-slate-300',
  active: 'bg-emerald-500/20 text-emerald-300',
  waiting: 'bg-amber-500/20 text-amber-300',
  review: 'bg-violet-500/20 text-violet-300',
  done: 'bg-blue-500/20 text-blue-300',
  paused: 'bg-slate-500/20 text-slate-300',
  conflict: 'bg-rose-500/20 text-rose-300',
};

const NAVIGATOR_NODE_ID = 'alexcreator_navigator';
const NAVIGATOR_TASK_TITLE = 'AlexCreator Navigator';
const NAVIGATOR_CONTEXT =
  'You are AlexCreator personal navigator for EvoPyramid OS. Help with onboarding, controls, architecture navigation, and practical next steps inside this UI.';

function AgentWorkspace({ sessionId, onClose, onSessionChange }: AgentWorkspaceProps) {
  const { sessions, loading, error, addMessage, loadSessions, updateStatus, deleteSession, openInBrowser, createSession } = useSessionRegistry();
  const [draft, setDraft] = useState('');
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId);
  const scrollRef = useRef<HTMLDivElement>(null);

  const sortedSessions = useMemo(
    () => [...sessions].sort((a, b) => b.updated_at.localeCompare(a.updated_at)),
    [sessions],
  );

  const activeSession = useMemo(
    () => (currentSessionId ? sortedSessions.find((session) => session.id === currentSessionId) ?? null : null),
    [currentSessionId, sortedSessions],
  );

  useEffect(() => {
    if (sessionId) {
      setCurrentSessionId(sessionId);
    }
  }, [sessionId]);

  useEffect(() => {
    void loadSessions();
    const poll = window.setInterval(() => {
      void loadSessions();
    }, 2000);
    return () => clearInterval(poll);
  }, [loadSessions]);

  useEffect(() => {
    if (!currentSessionId && sortedSessions.length > 0) {
      const nextId = sortedSessions[0].id;
      setCurrentSessionId(nextId);
      onSessionChange?.(nextId);
    }
  }, [currentSessionId, onSessionChange, sortedSessions]);

  useEffect(() => {
    if (!activeSession && currentSessionId && sortedSessions.length > 0) {
      const fallback = sortedSessions[0].id;
      setCurrentSessionId(fallback);
      onSessionChange?.(fallback);
    }
  }, [activeSession, currentSessionId, onSessionChange, sortedSessions]);

  useEffect(() => {
    if (!scrollRef.current) {
      return;
    }
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [activeSession?.messages.length]);

  const selectSession = (id: string) => {
    setCurrentSessionId(id);
    onSessionChange?.(id);
  };

  const send = async () => {
    if (!draft.trim() || !activeSession) {
      return;
    }
    const content = draft.trim();
    setDraft('');
    await addMessage(activeSession.id, content, 'user', true);
    window.setTimeout(() => {
      void loadSessions();
    }, 650);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await send();
  };

  const handleAutorun = async () => {
    if (!activeSession?.node_id) {
      return;
    }
    const response = await fetch(`${CORE_API_BASE}/node/${activeSession.node_id}/run`, { method: 'POST' });
    const data = await response.json();
    const text =
      data.status === 'success'
        ? `[AUTORUN SUCCESS]\n${data.output ?? ''}`
        : `[AUTORUN FAILED]\n${data.message ?? data.output ?? 'No output'}`;
    await addMessage(activeSession.id, text, 'assistant', false);
  };

  const setStatus = async (status: SessionStatus) => {
    if (!activeSession) {
      return;
    }
    await updateStatus(activeSession.id, status);
    window.setTimeout(() => {
      void loadSessions();
    }, 300);
  };

  const removeSession = async () => {
    if (!activeSession) {
      return;
    }
    const approved = window.confirm(`Delete session ${activeSession.id}?`);
    if (!approved) {
      return;
    }
    await deleteSession(activeSession.id);
    const next = sortedSessions.find((session) => session.id !== activeSession.id);
    const nextId = next?.id ?? null;
    setCurrentSessionId(nextId);
    if (nextId) {
      onSessionChange?.(nextId);
    }
  };

  const openNavigator = async () => {
    const existing = sortedSessions.find(
      (session) => session.node_id === NAVIGATOR_NODE_ID && session.provider === 'ollama',
    );
    if (existing) {
      selectSession(existing.id);
      return;
    }

    const created = await createSession({
      node_id: NAVIGATOR_NODE_ID,
      node_z: 17,
      node_sector: 'SPINE',
      provider: 'ollama',
      task_title: NAVIGATOR_TASK_TITLE,
      task_context: NAVIGATOR_CONTEXT,
      account_hint: 'AlexCreator',

    });

    if (created) {
      selectSession(created.id);
      await addMessage(
        created.id,
        'Start as my project navigator. Give me a compact onboarding: what to click first, how to create sessions, and how to sync structure.',
        'user',
        true,
      );
    }
  };

  if (sortedSessions.length === 0) {
    return (
      <section className="h-full bg-slate-950 text-slate-200 flex flex-col">
        <header className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-semibold">Assistant</h2>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-md hover:bg-white/10" title="Close">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </header>
        <div className="flex-1 flex flex-col items-center justify-center text-sm text-slate-400 p-8 text-center gap-4">
          <p>Create an agent session from a node card, or start a global AI navigator for AlexCreator.</p>
          <button
            onClick={() => {
              void openNavigator();
            }}
            className="px-3 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
          >
            Start AlexCreator Navigator
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="h-full bg-slate-950 text-slate-200 flex flex-col">
      <header className="px-4 py-3 border-b border-white/10">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <Bot className="w-4 h-4 text-emerald-400 shrink-0" />
            <h2 className="text-sm font-semibold truncate">Assistant Control</h2>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-md hover:bg-white/10" title="Close">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        <div className="mt-2">
          <select
            value={activeSession?.id ?? ''}
            onChange={(event) => selectSession(event.target.value)}
            className="w-full rounded-lg border border-white/10 bg-black/30 px-2.5 py-1.5 text-[11px] outline-none"
          >
            {sortedSessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.provider.toUpperCase()} • {session.task_title}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-2 flex items-center justify-between gap-2">
          <button
            onClick={() => {
              void openNavigator();
            }}
            className="text-[10px] px-2 py-1 rounded border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/20"
          >
            AlexCreator Navigator
          </button>
          <span className="text-[10px] text-slate-500">Global helper mode (Ollama)</span>
        </div>

        {activeSession && (
          <div className="mt-2 flex items-center gap-2 flex-wrap">
            <span className="text-[10px] font-mono text-slate-400">{activeSession.id}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${STATUS_STYLE[activeSession.status]}`}>{activeSession.status}</span>
            <button
              onClick={() => {
                void setStatus('active');
              }}
              className="text-[10px] px-1.5 py-0.5 rounded border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/20 inline-flex items-center gap-1"
            >
              <PlayCircle className="w-3 h-3" />
              Active
            </button>
            <button
              onClick={() => {
                void setStatus('paused');
              }}
              className="text-[10px] px-1.5 py-0.5 rounded border border-white/20 text-slate-300 hover:bg-white/10 inline-flex items-center gap-1"
            >
              <PauseCircle className="w-3 h-3" />
              Pause
            </button>
            <button
              onClick={() => {
                void setStatus('done');
              }}
              className="text-[10px] px-1.5 py-0.5 rounded border border-blue-500/40 text-blue-300 hover:bg-blue-500/20"
            >
              Done
            </button>
            <button
              onClick={removeSession}
              className="ml-auto text-[10px] px-1.5 py-0.5 rounded border border-rose-500/40 text-rose-300 hover:bg-rose-500/20 inline-flex items-center gap-1"
            >
              <Trash2 className="w-3 h-3" />
              Delete
            </button>
          </div>
        )}
      </header>

      {activeSession && (
        <>
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
            {activeSession.task_context && (
              <div className="rounded-xl border border-amber-500/25 bg-amber-500/10 p-3 text-xs text-amber-100">
                {activeSession.task_context}
              </div>
            )}

            {activeSession.messages.map((message) => (
              <div key={message.id} className={`flex gap-2 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.role !== 'user' && (
                  <div className="w-7 h-7 rounded-lg border border-white/10 bg-slate-900 flex items-center justify-center shrink-0">
                    <Bot className="w-3.5 h-3.5 text-emerald-300" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-xl px-3 py-2 text-sm whitespace-pre-wrap ${
                    message.role === 'user'
                      ? 'bg-emerald-600 text-white'
                      : message.role === 'assistant'
                        ? 'bg-slate-900 border border-white/10 text-slate-100'
                        : 'bg-slate-800 text-slate-300'
                  }`}
                >
                  {message.content}
                </div>

                {message.role === 'user' && (
                  <div className="w-7 h-7 rounded-lg border border-emerald-500/30 bg-emerald-500/20 flex items-center justify-center shrink-0">
                    <User className="w-3.5 h-3.5 text-emerald-200" />
                  </div>
                )}
              </div>
            ))}

            {loading && <div className="text-[11px] text-slate-400 animate-pulse">Loading session updates...</div>}
            {error && <div className="text-[11px] text-rose-300">{error}</div>}
          </div>

          <div className="border-t border-white/10 p-3">
            <form onSubmit={handleSubmit} className="relative">
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder={activeSession.node_id === NAVIGATOR_NODE_ID ? 'Ask AlexCreator Navigator...' : `Message ${activeSession.provider}...`}
                rows={2}
                className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 pr-12 text-sm outline-none resize-none focus:border-emerald-400"
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    void send();
                  }
                }}
              />
              <button
                type="submit"
                disabled={!draft.trim() || loading}
                className="absolute right-2 bottom-2 p-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500"
                title="Send"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>

            <div className="mt-2 flex items-center gap-2">
              <span className="text-[10px] text-slate-400 inline-flex items-center gap-1">
                <Terminal className="w-3 h-3" />
                Local agent bridge
              </span>
              <button
                onClick={handleAutorun}
                className="px-2.5 py-1 rounded-md text-[10px] font-semibold bg-amber-500/20 text-amber-200 border border-amber-500/30 hover:bg-amber-500/30 inline-flex items-center gap-1"
              >
                <Zap className="w-3 h-3" />
                Autorun
              </button>
              <button
                onClick={() => {
                  void openInBrowser(
                    activeSession.provider,
                    activeSession.task_title,
                    activeSession.node_id,
                    activeSession.external_url,
                  );
                }}
                className="px-2.5 py-1 rounded-md text-[10px] font-semibold bg-white/10 text-slate-200 border border-white/20 hover:bg-white/15 inline-flex items-center gap-1"
              >
                <ExternalLink className="w-3 h-3" />
                Open
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

export default AgentWorkspace;




