/**
 * AgentWorkspace
 * ──────────────
 * Unified EP-OS Dashboard for agent interaction.
 * Z7 · β-layer · RED sector
 */

import React, { useState, useEffect, useRef } from 'react';
import {
    Send, Bot, User, Code, Sparkles,
    Terminal, ShieldCheck, Zap, MoreHorizontal,
    LayoutGrid, MessageSquare
} from 'lucide-react';
import { AgentSession, Message, useSessionRegistry } from '../lib/useSessionRegistry';

interface Props {
    sessionId: string | null;
    onClose: () => void;
}

export default function AgentWorkspace({ sessionId, onClose }: Props) {
    const { sessions, loading, addMessage, loadSessions } = useSessionRegistry();
    const [input, setInput] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    const activeSession = sessions.find(s => s.id === sessionId);

    useEffect(() => {
        if (sessionId) loadSessions();
    }, [sessionId, loadSessions]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [activeSession?.messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || !sessionId) return;

        const text = input.trim();
        setInput('');

        // Send user message and trigger REAL AI
        await addMessage(sessionId, text, 'user', true);
    };

    if (!sessionId || !activeSession) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center bg-slate-50 text-slate-400">
                <LayoutGrid className="w-12 h-12 mb-4 opacity-20" />
                <p className="text-sm font-mono tracking-widest uppercase">Select a node to activate workspace</p>
            </div>
        );
    }

    return (
        <div className="flex-1 flex flex-col bg-white overflow-hidden border-l border-slate-200 shadow-2xl">

            {/* Workspace Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-white/80 backdrop-blur-md">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center border border-emerald-100">
                        <Bot className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                        <h2 className="text-base font-bold text-slate-900 leading-none">{activeSession.task_title}</h2>
                        <div className="flex items-center gap-2 mt-1.5">
                            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-tight">Active session:</span>
                            <span className="text-[10px] font-mono font-bold text-emerald-600">{activeSession.id}</span>
                            <span className="w-1 h-1 rounded-full bg-slate-300" />
                            <span className="text-[10px] font-mono text-slate-500 uppercase">{activeSession.provider}</span>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button title="Security Check" className="p-2 text-slate-400 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition-colors">
                        <ShieldCheck className="w-4 h-4" />
                    </button>
                    <button title="More Actions" className="p-2 text-slate-400 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition-colors">
                        <MoreHorizontal className="w-4 h-4" />
                    </button>
                    <button onClick={onClose} title="Close Workspace" className="ml-2 text-slate-400 hover:text-slate-900 font-bold text-lg">×</button>
                </div>
            </div>

            {/* Chat Area */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#fafafa]/50">

                {/* Task Context Banner */}
                {activeSession.node_id?.startsWith('gen-') && (
                    <div className="bg-slate-900 text-slate-100 rounded-2xl p-5 mb-4 border border-slate-700 shadow-xl">
                        <div className="flex items-center gap-2 mb-3">
                            <Code className="w-4 h-4 text-emerald-400" />
                            <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-emerald-400">EvoGenesis Blueprint: Async Video Stack</span>
                        </div>
                        <div className="space-y-3 text-[11px] font-mono leading-relaxed">
                            <p className="text-slate-400 italic border-l-2 border-emerald-500/30 pl-3">Architecture: GCP Cloud Run + Cloud Tasks + Replicate Webhooks</p>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                                    <span className="block text-emerald-400 mb-1">■ Core Logic (Z9)</span>
                                    <span>Replicate API Polling / Webhook Handler (FastAPI)</span>
                                </div>
                                <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                                    <span className="block text-emerald-400 mb-1">■ Queue (Z7)</span>
                                    <span>GCP Cloud Tasks (for reliable async retries)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeSession.task_context && !activeSession.node_id?.startsWith('gen-') && (
                    <div className="bg-amber-50/50 border border-amber-100 rounded-2xl p-4 flex gap-4">
                        <Sparkles className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                        <div className="text-sm text-amber-900/70 leading-relaxed italic">
                            {activeSession.task_context}
                        </div>
                    </div>
                )}

                {/* Messages */}
                {activeSession.messages.map((msg) => (
                    <div key={msg.id} className={`flex gap-4 ${msg.role === 'assistant' ? '' : 'flex-row-reverse'}`}>
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${msg.role === 'assistant' ? 'bg-white border-slate-200' : 'bg-emerald-500 border-emerald-400'
                            }`}>
                            {msg.role === 'assistant' ? <Bot className="w-4 h-4 text-slate-600" /> : <User className="w-4 h-4 text-white" />}
                        </div>
                        <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-sm ${msg.role === 'assistant'
                            ? 'bg-white text-slate-800 border border-slate-100'
                            : 'bg-emerald-500 text-white'
                            }`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4 animate-pulse">
                        <div className="w-8 h-8 rounded-lg bg-slate-100 shrink-0" />
                        <div className="h-10 bg-slate-100 rounded-2xl w-1/3" />
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="p-6 bg-white border-t border-slate-100">
                <form onSubmit={handleSend} className="relative">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={`Instruct ${activeSession.provider}...`}
                        rows={2}
                        className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-4 pr-12 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 transition-all resize-none"
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend(e);
                            }
                        }}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        title="Send Instruction"
                        className="absolute right-2 bottom-2 p-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-200 text-white rounded-xl transition-all shadow-md active:scale-95"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </form>
                <div className="flex items-center gap-4 mt-3">
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400 uppercase">
                        <Zap className="w-3 h-3 text-amber-500" />
                        <span>Layer Beta / Z9 Active</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400 uppercase">
                        <Terminal className="w-3 h-3" />
                        <span>Ready for command</span>
                    </div>
                    <button
                        onClick={async () => {
                            if (!activeSession.node_id) return;
                            const res = await fetch(`http://127.0.0.1:8000/node/${activeSession.node_id}/run`, { method: 'POST' });
                            const data = await res.json();
                            if (data.status === 'success') {
                                addMessage(sessionId, `[AUTORUN SUCCESS]\n${data.output}`, 'assistant', false);
                            } else {
                                addMessage(sessionId, `[AUTORUN FAILED]\n${data.message || data.output}`, 'assistant', false);
                            }
                        }}
                        className="ml-auto flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-600 rounded-lg text-[10px] font-bold transition-all border border-amber-500/20"
                    >
                        <Zap className="w-3 h-3" />
                        AUTORUN NODE
                    </button>
                </div>
            </div>
        </div>
    );
}
