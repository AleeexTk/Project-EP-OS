import React, { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';
import { SwarmEvent } from '../lib/useSwarmTerminal';

const PROVIDER_COLORS: Record<string, string> = {
  gpt: '#10a37f',
  gemini: '#4285f4',
  claude: '#f5a623',
  copilot: '#7c3aed',
  ollama: '#7c3aed',
  system: '#94a3b8',
};

function EventRow({ event }: { event: SwarmEvent }) {
  const ts = new Date(event.ts).toLocaleTimeString('uk-UA', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  const provider = event.provider ?? 'system';
  const color = PROVIDER_COLORS[provider] ?? PROVIDER_COLORS.system;

  const message =
    event.event === 'session.created'
      ? `Session ${event.session_id} attached to ${event.node_id}`
      : event.event === 'session.status_changed'
        ? `Status => ${event.new_status}`
        : event.content ?? 'System event';

  return (
    <div className="flex gap-2 text-[10px]">
      <span className="text-slate-500 shrink-0">[{ts}]</span>
      <span className="font-bold shrink-0 opacity-80">
        {provider.toUpperCase()}
      </span>
      <span className="text-slate-300">{message}</span>
    </div>
  );
}

interface SwarmTerminalPanelProps {
  open: boolean;
  connected: boolean;
  events: SwarmEvent[];
  onToggle: () => void;
}

export default function SwarmTerminalPanel({ open, connected, events, onToggle }: SwarmTerminalPanelProps) {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!terminalRef.current) return;
    terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
  }, [events]);

  return (
    <>
      <button
        onClick={onToggle}
        className={`absolute left-4 bottom-4 z-40 p-3 rounded-full border transition-colors ${
          open
            ? 'bg-emerald-500 border-emerald-400 text-black'
            : 'bg-slate-900 border-white/10 text-slate-300 hover:bg-slate-800'
        }`}
        title="Toggle swarm terminal"
      >
        <Terminal className="w-4 h-4" />
      </button>

      {open && (
        <div className="absolute left-4 bottom-20 z-40 w-[310px] h-[300px] rounded-2xl bg-slate-950 border border-white/10 shadow-2xl overflow-hidden">
          <div className="px-3 py-2 border-b border-white/10 text-[10px] flex items-center justify-between">
            <span className="font-semibold tracking-wide">Swarm Stream</span>
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          </div>
          <div
            ref={terminalRef}
            className="h-[258px] overflow-y-auto px-3 py-2 space-y-1.5 font-mono no-scrollbar"
          >
            {events.map((event) => (
              <EventRow key={event.id} event={event} />
            ))}
          </div>
        </div>
      )}
    </>
  );
}
