import React, { useState } from 'react';
import { Zap } from 'lucide-react';
import { EvoNode, getRadius, CENTER } from '../lib/evo';

interface ArchitectTableProps {
    nodes: EvoNode[];
    onSelectNode: (node: EvoNode) => void;
}

const ArchitectTable: React.FC<ArchitectTableProps> = ({ nodes, onSelectNode }) => {
    const [activeZ, setActiveZ] = useState<number>(17);

    // Filter levels (only structural ones for now: 17, 15, 13, 11, 9, 7, 5, 3, 1)
    const structuralLevels = [17, 15, 13, 11, 9, 7, 5, 3, 1];

    const r = getRadius(activeZ);
    const size = r * 2 + 1;
    const gridRange = Array.from({ length: size }, (_, i) => CENTER - r + i);

    const getGridColsClass = (s: number) => {
        const map: Record<number, string> = {
            1: 'grid-cols-1',
            3: 'grid-cols-3',
            5: 'grid-cols-5',
            7: 'grid-cols-7',
            9: 'grid-cols-9',
            11: 'grid-cols-11',
            13: 'grid-cols-13',
            15: 'grid-cols-15',
            17: 'grid-cols-17'
        };
        return map[s] || 'grid-cols-1';
    };

    const getCellNode = (x: number, y: number) => {
        return nodes.find(n => n.z === activeZ && n.x === x && n.y === y);
    };

    return (
        <div className="flex flex-col h-full bg-slate-900 text-slate-200 border border-slate-700 rounded-lg overflow-hidden shadow-2xl">
            {/* Tabs */}
            <div className="flex bg-slate-800 border-b border-slate-700 overflow-x-auto no-scrollbar">
                {structuralLevels.map(z => (
                    <button
                        key={z}
                        onClick={() => setActiveZ(z)}
                        className={`px-4 py-2 text-xs font-mono transition-colors whitespace-nowrap ${activeZ === z
                            ? 'bg-blue-600 text-white border-b-2 border-blue-400'
                            : 'hover:bg-slate-700 text-slate-400'
                            } `}
                    >
                        Z{z} ({getRadius(z) * 2 + 1}x{getRadius(z) * 2 + 1})
                    </button>
                ))}
            </div>

            {/* Grid */}
            <div className="flex-1 p-6 overflow-auto bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-800 to-slate-950">
                <div
                    className={`grid gap-2 mx-auto ${getGridColsClass(size)} w-fit`}
                >
                    {gridRange.map(y => (
                        gridRange.map(x => {
                            const node = getCellNode(x, y);
                            const isEmpty = !node || node.kind === 'empty';

                            return (
                                <div
                                    key={`${x}-${y}`}
                                    onClick={() => node && onSelectNode(node)}
                                    aria-label={node?.label || `Empty slot at ${x},${y}`}
                                    className={`
                    group relative p-3 h-24 rounded border transition-all cursor-pointer flex flex-col justify-between
                    ${isEmpty
                                            ? 'border-slate-800 bg-slate-900/50 hover:border-slate-600 opacity-40'
                                            : 'border-blue-500/30 bg-blue-900/10 hover:bg-blue-900/20 hover:scale-[1.02] shadow-lg shadow-blue-500/5'
                                        }
`}
                                >
                                    <div className="flex justify-between items-start">
                                        <span className="text-[10px] font-mono opacity-50">{x},{y}</span>
                                        {!isEmpty && (
                                            <div className="flex items-center gap-1.5">
                                                <button
                                                    onClick={async (e) => {
                                                        e.stopPropagation();
                                                        await fetch(`http://127.0.0.1:8000/node/${node.id}/run`, { method: 'POST' });
                                                    }}
                                                    title="Autorun Node"
                                                    className="p-1.5 bg-amber-500/20 text-amber-500 rounded hover:bg-amber-500/40 transition-colors opacity-0 group-hover:opacity-100"
                                                >
                                                    <Zap className="w-2.5 h-2.5" />
                                                </button >
                                                <div
                                                    className={`w-2 h-2 rounded-full ${node.status === 'active' ? 'bg-emerald-500' : 'bg-slate-400'}`}
                                                />
                                            </div >
                                        )}
                                    </div >

                                    <div className="mt-1">
                                        <div className="text-[11px] font-bold truncate leading-tight">
                                            {node?.label || 'EMPTY SLOT'}
                                        </div>
                                        {!isEmpty && (
                                            <div className="text-[9px] opacity-60 uppercase tracking-tighter mt-1">
                                                {node.kind} / {node.sector}
                                            </div>
                                        )}
                                    </div>

                                    {
                                        !isEmpty && node.agentRole && (
                                            <div className="text-[8px] bg-blue-500/20 text-blue-300 px-1 py-0.5 rounded mt-2 truncate">
                                                {node.agentRole}
                                            </div>
                                        )
                                    }
                                </div >
                            );
                        })
                    ))}
                </div >
            </div >

            {/* Footer Info */}
            < div className="p-3 bg-slate-900 border-t border-slate-700 text-[10px] flex justify-between items-center opacity-70" >
                <div className="font-mono">PROJECT: EVOPYRAMID OS | LAYER: {activeZ >= 11 ? 'ALPHA' : activeZ >= 5 ? 'BETA' : 'GAMMA'}</div>
                <div>TOTAL NODES AT THIS LEVEL: {size * size}</div>
            </div >
        </div >
    );
};

export default ArchitectTable;
