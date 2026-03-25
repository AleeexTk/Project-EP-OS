import React from 'react';
import { RefreshCw, ShieldCheck } from 'lucide-react';

type ViewMode = 'structure' | 'directory' | 'active' | 'collaboration' | 'canon';

interface SidebarControlsProps {
  panX: number;
  panY: number;
  activeZLevel: number;
  viewMode: ViewMode;
  syncingStructure: boolean;
  guardingCanon: boolean;
  onPanXChange: (val: number) => void;
  onPanYChange: (val: number) => void;
  onZLevelChange: (val: number) => void;
  onViewModeChange: (mode: ViewMode) => void;
  onSync: () => void;
  onGuard: () => void;
}

const SidebarControls: React.FC<SidebarControlsProps> = ({
  panX,
  panY,
  activeZLevel,
  viewMode,
  syncingStructure,
  guardingCanon,
  onPanXChange,
  onPanYChange,
  onZLevelChange,
  onViewModeChange,
  onSync,
  onGuard
}) => {
  return (
    <>
      {/* Vertical Sliders (Left) */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 z-30 hidden md:flex flex-col items-center gap-3 p-3 rounded-2xl bg-black/30 border border-white/10 backdrop-blur-md shadow-xl transition-all duration-300 hover:bg-black/40">
        <div className="flex flex-col items-center gap-1">
          <input
            type="range"
            min={0}
            max={100}
            value={panY}
            onChange={(e) => onPanYChange(Number(e.target.value))}
            aria-label="Pan Y"
            className="slider-vertical h-32 w-1.5"
          />
          <span className="text-[9px] font-bold text-slate-500">PAN-Y</span>
        </div>
        
        <div className="w-full h-px bg-white/10 my-1" />

        <div className="flex flex-col items-center gap-1">
          <input
            type="range"
            min={0}
            max={17}
            step={1}
            value={activeZLevel}
            onChange={(e) => onZLevelChange(Number(e.target.value))}
            aria-label="Z level"
            className="slider-vertical h-32 w-1.5"
          />
          <span className="text-[10px] font-mono font-bold text-emerald-400">{activeZLevel === 0 ? 'ALL' : `Z${activeZLevel}`}</span>
        </div>
      </div>

      {/* Horizontal Pan (Bottom) */}
      <div className="absolute left-1/2 -translate-x-1/2 bottom-6 z-30 w-[40%] hidden md:block">
        <div className="px-4 py-2 rounded-full bg-black/30 border border-white/10 backdrop-blur-md shadow-lg">
          <input
            type="range"
            min={0}
            max={100}
            value={panX}
            onChange={(e) => onPanXChange(Number(e.target.value))}
            aria-label="Pan X"
            className="w-full h-1 bg-emerald-500/20 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
        </div>
      </div>

      {/* View Mode & Actions (Top Right) */}
      <div className="absolute right-4 top-[100px] z-40 rounded-xl bg-black/40 border border-white/10 px-3 py-2 backdrop-blur-md shadow-xl">
        <div className="flex items-center gap-3">
          <div className="flex flex-col">
            <span className="text-[8px] uppercase font-bold text-slate-500 mb-0.5">Perspective</span>
            <select
              value={viewMode}
              title="Pyramid View Mode"
              onChange={(e) => onViewModeChange(e.target.value as ViewMode)}
              className="bg-transparent text-[11px] text-slate-200 outline-none cursor-pointer font-medium hover:text-white transition-colors"
            >
              <option value="structure">Structure</option>
              <option value="directory">Directory</option>
              <option value="active">Active</option>
              <option value="collaboration">Collaboration</option>
              <option value="canon">Canon</option>
            </select>
          </div>

          <div className="flex items-center gap-2 border-l border-white/10 pl-3">
            <button
              onClick={onSync}
              disabled={syncingStructure}
              className="px-2.5 py-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-[10px] font-bold inline-flex items-center gap-1.5 hover:bg-emerald-500/20 active:scale-95 transition-all disabled:opacity-50"
              title="Sync missing modules from project structure"
            >
              <RefreshCw className={`w-3 h-3 ${syncingStructure ? 'animate-spin' : ''}`} />
              {syncingStructure ? 'SYNCING' : 'SYNC'}
            </button>
            <button
              onClick={onGuard}
              disabled={guardingCanon}
              className="px-2.5 py-1.5 rounded-lg border border-blue-500/30 bg-blue-500/10 text-blue-300 text-[10px] font-bold inline-flex items-center gap-1.5 hover:bg-blue-500/20 active:scale-95 transition-all disabled:opacity-50"
              title="Canon guard: validate and align pyramid with folder structure"
            >
              <ShieldCheck className={`w-3 h-3 ${guardingCanon ? 'animate-pulse' : ''}`} />
              {guardingCanon ? 'GUARDING' : 'GUARD'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default SidebarControls;
