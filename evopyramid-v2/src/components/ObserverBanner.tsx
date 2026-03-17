import React from 'react';
import { ShieldCheck, Sparkles } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';

interface ObserverBannerProps {
  visible: boolean;
  onClose: () => void;
  onNotice: (msg: string) => void;
  onInspectNode: (nodeId: string) => void;
}

export default function ObserverBanner({ visible, onClose, onNotice, onInspectNode }: ObserverBannerProps) {
  if (!visible) return null;

  const handleQuarantine = async () => {
    try {
      const res = await fetch(`${CORE_API_BASE}/nodes/chaos_engine/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'quarantined' }),
      });
      if (!res.ok) throw new Error();
      onNotice('Z7 Quarantined successfully');
      onClose();
    } catch {
      onNotice('Failed to quarantine Z7');
    }
  };

  return (
    <div className="absolute top-28 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-[650px] bg-rose-950/80 border border-rose-500/50 rounded-lg p-3 text-[11px] flex flex-col md:flex-row items-center gap-3 backdrop-blur shadow-2xl">
      <div className="flex items-start md:items-center gap-3 text-rose-200">
        <Sparkles className="w-4 h-4 text-rose-400 shrink-0 mt-0.5 md:mt-0" />
        <div className="flex flex-col">
          <span className="font-semibold uppercase tracking-wider text-rose-400">Observer Alert</span>
          <span className="opacity-90 mt-0.5">
            Architectural anomaly detected in Z7. Awaiting manual routing confirmation.
          </span>
        </div>
      </div>
      <div className="flex flex-wrap md:flex-nowrap gap-2 md:ml-auto w-full md:w-auto mt-2 md:mt-0 justify-end">
        <button
          onClick={onClose}
          className="px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/50 text-rose-200 rounded-md font-semibold transition whitespace-nowrap flex-1 md:flex-none"
        >
          Confirm Route
        </button>
        <button
          onClick={handleQuarantine}
          className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-md font-semibold transition flex items-center justify-center gap-1 whitespace-nowrap flex-1 md:flex-none"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          Quarantine
        </button>
        <button
          onClick={() => onInspectNode('chaos_engine')}
          className="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-slate-300 rounded-md transition"
          title="Inspect Z7"
        >
          Inspect
        </button>
      </div>
    </div>
  );
}
