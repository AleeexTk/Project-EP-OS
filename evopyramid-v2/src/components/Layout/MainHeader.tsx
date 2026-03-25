import React from 'react';
import { Activity, Layers3, PanelRightOpen, Radar } from 'lucide-react';
import KernelMonitor from '../KernelMonitor';

interface MainHeaderProps {
  isConnected: boolean;
  swarmConnected: boolean;
  healthPct: number | null;
  memoryBlocks: number;
  activeSessionCount: number;
  totalSessions: number;
  onOpenAssistant: () => void;
}

const MainHeader: React.FC<MainHeaderProps> = ({
  isConnected,
  swarmConnected,
  healthPct,
  memoryBlocks,
  activeSessionCount,
  totalSessions,
  onOpenAssistant
}) => {
  return (
    <header className="absolute top-0 left-0 right-0 z-40 px-4 md:px-6 py-4 flex items-center justify-between pointer-events-none">
      <div className="pointer-events-auto">
        <div className="flex items-center gap-2">
          <Radar className="w-4 h-4 text-emerald-400" />
          <h1 className="text-sm md:text-base font-semibold tracking-wide">EP-OS Global Control Plane</h1>
        </div>
        <p className="text-[10px] text-slate-400 mt-0.5">Consolidated Web Control Plane | Local AI Runtime Orchestration</p>
      </div>

      <div className="flex items-center gap-2 md:gap-3 pointer-events-auto">
        <KernelMonitor />
        
        {/* Universal LLM Metrics Widget */}
        {(healthPct !== null || memoryBlocks > 0) && (
          <div className="hidden md:flex items-center gap-3 text-[10px] px-3 py-1.5 rounded-full bg-black/40 border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)] backdrop-blur-md">
            {healthPct !== null && (
              <div className="flex items-center gap-1.5" title="System Health (ObserverRelay)">
                <Activity className={`w-3.5 h-3.5 ${healthPct >= 90 ? 'text-emerald-400' : healthPct >= 60 ? 'text-amber-400' : 'text-rose-400'}`} />
                <span className="font-mono text-slate-200">{healthPct}%</span>
              </div>
            )}
            {healthPct !== null && memoryBlocks > 0 && <span className="text-slate-600">|</span>}
            {memoryBlocks > 0 && (
              <div className="flex items-center gap-1.5" title="Cognitive Cortex Size (Blocks)">
                <Layers3 className="w-3.5 h-3.5 text-blue-400" />
                <span className="font-mono text-slate-200">{memoryBlocks} ENG</span>
              </div>
            )}
          </div>
        )}

        <div className="hidden md:flex items-center gap-2 text-[10px] px-2.5 py-1 rounded-full bg-black/30 border border-white/10 backdrop-blur-sm transition-all duration-300">
          <div className="flex items-center gap-1.5" title="Core Connection Status">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500 shadow-[0_0_8px_#f43f5e] animate-pulse'}`} />
            <span className={isConnected ? 'text-slate-300' : 'text-rose-400 font-bold'}>{isConnected ? 'CORE' : 'CORE OFFLINE'}</span>
          </div>
          <span className="text-white/10 mx-0.5">|</span>
          <div className="flex items-center gap-1.5" title="Swarm Network Status">
            <span className={`w-2 h-2 rounded-full ${swarmConnected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-500/50'}`} />
            <span className={swarmConnected ? 'text-slate-300' : 'text-slate-500'}>SWARM</span>
          </div>
          <span className="text-white/10 mx-0.5 ml-1">|</span>
          <div className="flex items-center gap-1 px-1">
            <span className="text-emerald-400/80 font-mono">{activeSessionCount}</span>
            <span className="text-white/20">/</span>
            <span className="text-slate-400 font-mono">{totalSessions}</span>
          </div>
        </div>
        
        <button
          onClick={onOpenAssistant}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all duration-200 hover:scale-105 active:scale-95 shadow-lg group"
          title="Open assistant"
        >
          <PanelRightOpen className="w-4 h-4 text-slate-300 group-hover:text-white" />
        </button>
      </div>
    </header>
  );
};

export default MainHeader;
