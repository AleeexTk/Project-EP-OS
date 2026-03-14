/**
 * SessionLauncher
 * ───────────────
 * Modal panel for creating a new agent session on the selected pyramid node.
 * Lets the user choose provider, account hint, and task title.
 */

import React, { useState, useEffect } from 'react';
import { X, ExternalLink, Loader2, Bot, Zap } from 'lucide-react';
import {
    useSessionRegistry,
    Provider,
    SessionCreatePayload,
    ProviderInfo,
} from '../lib/useSessionRegistry';
import { EvoNode } from '../lib/evo';

interface Props {
    node: EvoNode;
    onClose: () => void;
    onCreated?: (sessionId: string, externalUrl?: string) => void;
}

const PROVIDER_LABELS: Record<Provider, string> = {
    gpt: 'ChatGPT / GPT-4o',
    gemini: 'Google Gemini',
    claude: 'Anthropic Claude',
    copilot: 'GitHub Copilot',
    ollama: 'Ollama (Local)',
};

const PROVIDER_ORDER: Provider[] = ['gpt', 'gemini', 'claude', 'copilot', 'ollama'];

const HEX_TO_BG_CLASS: Record<string, string> = {
    '#10a37f': 'bg-[#10a37f]',
    '#4285f4': 'bg-[#4285f4]',
    '#f5a623': 'bg-[#f5a623]',
    '#7c3aed': 'bg-[#7c3aed]',
    '#94a3b8': 'bg-[#94a3b8]',
};

export default function SessionLauncher({ node, onClose, onCreated }: Props) {
    const { createSession, loadProviders, providers, loading, openInBrowser } = useSessionRegistry();

    const [provider, setProvider] = useState<Provider>('gemini');
    const [taskTitle, setTaskTitle] = useState('');
    const [taskCtx, setTaskCtx] = useState('');
    const [account, setAccount] = useState('');
    const [launched, setLaunched] = useState(false);
    const [session, setSession] = useState<{ id: string; url?: string } | null>(null);

    useEffect(() => { loadProviders(); }, [loadProviders]);

    const selectedProvider: ProviderInfo | undefined = providers[provider];

    const handleCreate = async () => {
        if (!taskTitle.trim()) return;
        const payload: SessionCreatePayload = {
            node_id: node.id,
            node_z: node.z,
            node_sector: node.sector,
            provider,
            task_title: taskTitle.trim(),
            task_context: taskCtx.trim() || undefined,
            account_hint: account.trim() || undefined,
        };
        const s = await createSession(payload);
        if (s) {
            setSession({ id: s.id, url: s.external_url ?? undefined });
            onCreated?.(s.id, s.external_url ?? undefined);
            setLaunched(true);
        }
    };

    const handleOpen = () => {
        if (session?.url) {
            window.open(session.url, '_blank', 'noopener,noreferrer');
        } else {
            openInBrowser(provider, taskTitle, node.id);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-end justify-center sm:items-center bg-black/20 backdrop-blur-[2px]">
            <div className="w-full max-w-md bg-white rounded-t-3xl sm:rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">

                {/* Header */}
                <div className="flex items-center justify-between px-5 pt-5 pb-3 border-b border-slate-100">
                    <div>
                        <div className="flex items-center gap-2">
                            <Bot className="w-4 h-4 text-emerald-600" />
                            <span className="font-bold text-slate-900 text-sm">New Agent Session</span>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5 font-mono">
                            Node: <span className="text-slate-800">{node.label}</span> · Z{node.z} · {node.sector.toUpperCase()}
                        </p>
                    </div>
                    <button onClick={onClose} className="p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors" title="Close">
                        <X className="w-4 h-4" />
                    </button>
                </div>

                {!launched ? (
                    <div className="p-5 space-y-4">
                        {/* Provider selector */}
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 block">AI Provider</label>
                            <div className="grid grid-cols-2 gap-2">
                                {PROVIDER_ORDER.map(p => {
                                    const info = providers[p];
                                    const active = provider === p;
                                    return (
                                        <button
                                            key={p}
                                            onClick={() => setProvider(p)}
                                            className={`flex items-center gap-2 px-3 py-2.5 rounded-xl border text-left transition-all ${active
                                                ? 'border-emerald-400 bg-emerald-50 shadow-sm'
                                                : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                                                }`}
                                        >
                                            <span
                                                className={`w-2.5 h-2.5 rounded-full shrink-0 ${HEX_TO_BG_CLASS[info?.color_primary ?? '#888'] || 'bg-slate-400'}`}
                                            />
                                            <span className={`text-xs font-medium ${active ? 'text-emerald-800' : 'text-slate-700'}`}>
                                                {PROVIDER_LABELS[p]}
                                            </span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Task title */}
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">
                                Task Title <span className="text-red-400">*</span>
                            </label>
                            <input
                                type="text"
                                value={taskTitle}
                                onChange={e => setTaskTitle(e.target.value)}
                                placeholder={`e.g. Review Z${node.z} routing logic`}
                                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                            />
                        </div>

                        {/* Task context */}
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">Context / Brief</label>
                            <textarea
                                value={taskCtx}
                                onChange={e => setTaskCtx(e.target.value)}
                                placeholder="Optional: describe what you need from this agent..."
                                rows={3}
                                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 resize-none"
                            />
                        </div>

                        {/* Account hint */}
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">Account (optional)</label>
                            <input
                                type="text"
                                value={account}
                                onChange={e => setAccount(e.target.value)}
                                placeholder="e.g. work@gmail.com"
                                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-400"
                            />
                        </div>

                        {/* Action */}
                        <button
                            onClick={handleCreate}
                            disabled={!taskTitle.trim() || loading}
                            className="w-full bg-emerald-500 disabled:bg-slate-200 disabled:text-slate-400 hover:bg-emerald-600 active:bg-emerald-700 text-white font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-sm text-sm"
                        >
                            {loading ? (
                                <><Loader2 className="w-4 h-4 animate-spin" /> Creating session…</>
                            ) : (
                                <><Zap className="w-4 h-4" /> Create &amp; Bind to Node</>
                            )}
                        </button>
                    </div>
                ) : (
                    /* Success screen */
                    <div className="p-5 text-center space-y-4">
                        <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mx-auto">
                            <Zap className="w-6 h-6 text-emerald-600" />
                        </div>
                        <div>
                            <p className="font-bold text-slate-900">Session created!</p>
                            <p className="text-xs text-slate-500 font-mono mt-0.5">{session?.id}</p>
                        </div>
                        <p className="text-sm text-slate-600">
                            Node <span className="font-bold">{node.label}</span> is now marked as{' '}
                            <span className="text-emerald-600 font-bold">ACTIVE</span> in the Session Registry.
                        </p>
                        <div className="flex gap-2">
                            <button
                                onClick={handleOpen}
                                className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 text-sm transition-colors"
                            >
                                <ExternalLink className="w-4 h-4" />
                                Open {PROVIDER_LABELS[provider]}
                            </button>
                            <button
                                onClick={onClose}
                                className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 text-sm font-medium"
                            >
                                Done
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
