import React, { useEffect, useState } from 'react';
import { ShieldCheck, Activity, AlertCircle } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';

export default function KernelMonitor() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    const fetchKernel = async () => {
      try {
        const r = await fetch(`${CORE_API_BASE}/health/kernel`);
        if (r.ok) setStatus(await r.json());
      } catch {
        setStatus(null);
      }
    };
    fetchKernel();
    const t = setInterval(fetchKernel, 15000);
    return () => clearInterval(t);
  }, []);

  if (!status) return null;

  const hasViolations = status.audit_violations > 0;

  return (
    <div className="flex items-center gap-2 px-2 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px]">
      <div className="relative">
        <Activity className={`w-3.5 h-3.5 ${status.status === 'ONLINE' ? 'text-blue-400 animate-pulse' : 'text-slate-500'}`} />
        {hasViolations && (
          <div className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full animate-ping" />
        )}
      </div>
      <span className="font-bold text-blue-200 tracking-tighter">NUCLEUS V2</span>
      <span className="text-slate-500">|</span>
      {hasViolations ? (
        <span className="text-rose-400 font-bold flex items-center gap-1">
          <AlertCircle className="w-3 h-3" />
          VIOLATIONS: {status.audit_violations}
        </span>
      ) : (
        <span className="text-emerald-400 font-medium">PROTECTED</span>
      )}
    </div>
  );
}
