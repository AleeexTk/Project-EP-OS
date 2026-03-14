import React, { useEffect, useState } from 'react';
import { Bot, Loader2, X, Zap } from 'lucide-react';
import { EvoNode } from '../lib/evo';
import { Provider, SessionCreatePayload, useSessionRegistry } from '../lib/useSessionRegistry';

interface SessionLauncherProps {
  node: EvoNode;
  onClose: () => void;
  onCreated?: (sessionId: string, externalUrl?: string) => void;
}

const PROVIDER_LABELS: Record<Provider, string> = {
  gpt: 'ChatGPT',
  gemini: 'Gemini',
  claude: 'Claude',
  copilot: 'Copilot',
  ollama: 'Ollama',
};

const PROVIDER_ORDER: Provider[] = ['gemini', 'gpt', 'claude', 'copilot', 'ollama'];

function SessionLauncher({ node, onClose, onCreated }: SessionLauncherProps) {
  const { createSession, loadProviders, providers, loading } = useSessionRegistry();
  const [provider, setProvider] = useState<Provider>('gemini');
  const [taskTitle, setTaskTitle] = useState('');
  const [taskContext, setTaskContext] = useState('');
  const [accountHint, setAccountHint] = useState('');
  const [existingUrl, setExistingUrl] = useState('');

  useEffect(() => {
    void loadProviders();
  }, [loadProviders]);
  const providerUrlHint =
    provider === 'gpt'
      ? 'https://chatgpt.com/c/...'
      : provider === 'gemini'
        ? 'https://aistudio.google.com/...'
        : provider === 'claude'
          ? 'https://claude.ai/chat/...'
          : provider === 'copilot'
            ? 'https://github.com/copilot/...'
            : 'http://localhost:11434';

  const handleCreate = async () => {
    if (!taskTitle.trim()) {
      return;
    }
    const attachedUrl = existingUrl.trim();
    const payload: SessionCreatePayload = {
      node_id: node.id,
      node_z: node.z,
      node_sector: node.sector,
      provider,
      task_title: taskTitle.trim(),
      task_context: taskContext.trim() || undefined,
      account_hint: accountHint.trim() || undefined,
      external_url: attachedUrl || undefined,
    };
    const session = await createSession(payload);
    if (session) {
      onCreated?.(session.id, session.external_url);
    }
  };

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-900 text-slate-100 shadow-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-white/10 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-semibold">Create Agent Session</h2>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              Node: {node.label} вЂў Z{node.z} вЂў {node.sector.toUpperCase()}
            </p>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-white/10" title="Close">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <label className="text-[11px] text-slate-400 uppercase tracking-wide">Provider</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
              {PROVIDER_ORDER.map((id) => {
                const active = provider === id;
                const providerColor = providers[id]?.color_primary ?? '#94a3b8';
                return (
                  <button
                    key={id}
                    onClick={() => setProvider(id)}
                    className={`px-3 py-2 rounded-lg border text-[12px] transition-colors ${active ? 'border-emerald-400 bg-emerald-500/10 text-emerald-100' : 'border-white/10 bg-black/20 text-slate-300 hover:bg-white/5'}`}
                  >
                    <span className="inline-flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: providerColor }} />
                      {PROVIDER_LABELS[id]}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="text-[11px] text-slate-400 uppercase tracking-wide">Task title</label>
            <input
              value={taskTitle}
              onChange={(event) => setTaskTitle(event.target.value)}
              placeholder="Describe what the assistant should do"
              className="mt-2 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-emerald-400"
            />
          </div>

          <div>
            <label className="text-[11px] text-slate-400 uppercase tracking-wide">Task context</label>
            <textarea
              value={taskContext}
              onChange={(event) => setTaskContext(event.target.value)}
              rows={3}
              placeholder="Optional architecture brief"
              className="mt-2 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none resize-none focus:border-emerald-400"
            />
          </div>

          <div>
            <label className="text-[11px] text-slate-400 uppercase tracking-wide">Account hint</label>
            <input
              value={accountHint}
              onChange={(event) => setAccountHint(event.target.value)}
              placeholder="Optional email/account label"
              className="mt-2 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-emerald-400"
            />
          </div>

          <div>
            <label className="text-[11px] text-slate-400 uppercase tracking-wide">Attach existing browser session URL</label>
            <input
              value={existingUrl}
              onChange={(event) => setExistingUrl(event.target.value)}
              placeholder={providerUrlHint}
              className="mt-2 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-emerald-400"
            />
            <p className="mt-1 text-[10px] text-slate-500">
              Optional. Paste an existing chat URL (for example a chatgpt.com/c/... link) to attach it to this session.
            </p>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-white/10">
          <button
            onClick={handleCreate}
            disabled={loading || !taskTitle.trim()}
            className="w-full rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-400 px-4 py-2.5 text-sm font-semibold flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                Create Session
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default SessionLauncher;

