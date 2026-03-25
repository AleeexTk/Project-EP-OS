import React, { useEffect, useState } from 'react';
import { ShieldCheck, Activity, AlertCircle } from 'lucide-react';
import { usePyramidState } from '../lib/usePyramidState';

export default function KernelMonitor() {
  const { isConnected, systemMetrics } = usePyramidState();
  const [violations, setViolations] = useState(0);

  useEffect(() => {
    if (systemMetrics?.audit_violations !== undefined) {
      setViolations(systemMetrics.audit_violations);
    }
  }, [systemMetrics]);

  if (!isConnected) return null;

  const hasViolations = violations > 0;

  return (
    <div className={`flex items-center gap-2 px-2 py-1 rounded-full transition-all duration-500 border ${hasViolations ? 'bg-rose-500/10 border-rose-500/30' : 'bg-blue-500/10 border-blue-500/20'} text-[10px]`}>
      <div className="relative">
        <Activity className={`w-3.5 h-3.5 ${isConnected ? 'text-blue-400 animate-pulse' : 'text-slate-500'}`} />
        {hasViolations && (
          <div className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full animate-ping" />
        )}
      </div>
      <span className="font-bold text-blue-200 tracking-tighter">NUCLEUS V2</span>
      <span className="text-slate-500">|</span>
      {hasViolations ? (
        <span className="text-rose-400 font-bold flex items-center gap-1">
          <AlertCircle className="w-3 h-3" />
          VIOLATIONS: {violations}
        </span>
      ) : (
        <span className="text-emerald-400 font-medium">PROTECTED</span>
      )}
    </div>
  );
}
