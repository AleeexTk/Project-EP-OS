import React, { useMemo, useState } from 'react';
import { Play } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';
import { CENTER, EvoNode, getRadius } from '../lib/evo';

interface ArchitectTableProps {
  nodes: EvoNode[];
  onSelectNode: (node: EvoNode) => void;
}

const ALL_LEVELS = [17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1];

const GRID_CLASS: Record<number, string> = {
  1: 'grid-cols-1',
  3: 'grid-cols-3',
  5: 'grid-cols-5',
  7: 'grid-cols-7',
  9: 'grid-cols-9',
  11: 'grid-cols-11',
  13: 'grid-cols-13',
  15: 'grid-cols-15',
  17: 'grid-cols-17',
};

function ArchitectTable({ nodes, onSelectNode }: ArchitectTableProps) {
  const [activeZ, setActiveZ] = useState<number>(17);
  const radius = getRadius(activeZ);
  const size = radius * 2 + 1;
  const gridRange = useMemo(() => Array.from({ length: size }, (_, index) => CENTER - radius + index), [radius, size]);

  const getCellNode = (x: number, y: number) => nodes.find((node) => node.z === activeZ && node.x === x && node.y === y);

  return (
    <div className="h-full rounded-2xl overflow-hidden border border-white/10 bg-slate-900 shadow-2xl flex flex-col">
      <div className="border-b border-white/10 bg-slate-950/80 overflow-x-auto no-scrollbar">
        <div className="flex min-w-max">
          {ALL_LEVELS.map((zLevel) => (
            <button
              key={zLevel}
              onClick={() => setActiveZ(zLevel)}
              className={`px-4 py-2 text-[11px] font-mono transition-colors ${activeZ === zLevel ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
            >
              Z{zLevel}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.15),_rgba(2,6,23,1))]">
        <div className={`grid gap-2 mx-auto w-fit ${GRID_CLASS[size] ?? 'grid-cols-1'}`}>
          {gridRange.map((y) =>
            gridRange.map((x) => {
              const node = getCellNode(x, y);
              const empty = !node || node.kind === 'empty';

              return (
                <button
                  key={`${x}-${y}`}
                  onClick={() => node && onSelectNode(node)}
                  className={`group relative h-24 p-2 rounded-xl text-left transition-all border ${
                    empty
                      ? 'border-slate-800 bg-black/20 hover:border-slate-600'
                      : 'border-blue-500/30 bg-blue-900/20 hover:bg-blue-800/30 hover:border-blue-400/50'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span>
                      {x},{y}
                    </span>
                    {!empty && node && (
                      <button
                        onClick={async (event) => {
                          event.stopPropagation();
                          await fetch(`${CORE_API_BASE}/node/${node.id}/run`, { method: 'POST' });
                        }}
                        title="Autorun node"
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500/30"
                      >
                        <Play className="w-3 h-3" />
                      </button>
                    )}
                  </div>

                  <div className="mt-2">
                    <div className={`text-[11px] font-semibold truncate ${empty ? 'text-slate-500' : 'text-slate-100'}`}>
                      {node?.label ?? 'EMPTY SLOT'}
                    </div>
                    {!empty && node && (
                      <div className="mt-1 text-[9px] uppercase tracking-wide text-slate-400">
                        {node.kind} / {node.sector}
                      </div>
                    )}
                  </div>
                </button>
              );
            }),
          )}
        </div>
      </div>

      <div className="px-4 py-2 border-t border-white/10 text-[10px] text-slate-400 flex items-center justify-between">
        <span className="font-mono">LAYER: {activeZ >= 11 ? 'ALPHA' : activeZ >= 5 ? 'BETA' : 'GAMMA'}</span>
        <span>{size * size} cells</span>
      </div>
    </div>
  );
}

export default ArchitectTable;
