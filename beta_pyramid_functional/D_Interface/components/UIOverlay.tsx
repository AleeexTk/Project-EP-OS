
import React from 'react';
import { EvoNode, SECTOR_COLORS, STATUS_COLORS } from '../lib/evo';
import { Info, Layers, Box, Cpu, Activity, Shield, Zap, Database, Network, Map } from 'lucide-react';

interface UIOverlayProps {
  selectedNode: EvoNode | null;
  onClose: () => void;
}

export default function UIOverlay({ selectedNode, onClose }: UIOverlayProps) {
  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-6">
      {/* Header */}
      <div className="flex justify-between items-start pointer-events-auto">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tighter">EVO<span className="text-emerald-600">PYRAMID</span> OS</h1>
          <p className="text-slate-500 text-sm font-mono mt-1">v1.0 // PART 4: ARCHITECTURE & ROADMAP</p>

          {/* Roadmap Panel */}
          <div className="bg-white/80 backdrop-blur border border-slate-200 p-4 rounded-xl shadow-sm mt-4 w-64">
            <h3 className="text-slate-600 text-xs font-mono uppercase mb-3 flex items-center gap-2">
              <Map className="w-3 h-3 text-emerald-500" /> Roadmap Status
            </h3>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between items-center">
                <span className="text-slate-900 font-bold">Phase A: Core</span>
                <span className="text-emerald-600">EXISTS</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-900 font-bold">Phase B: α/β</span>
                <span className="text-amber-500">PARTIAL</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Phase C: γ Sync</span>
                <span className="text-slate-400">PLANNED</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Phase D: Input/Z1</span>
                <span className="text-slate-400">PLANNED</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          {/* System Monitor */}
          <div className="bg-white/80 backdrop-blur border border-slate-200 p-4 rounded-xl w-64 shadow-sm">
            <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
              <h3 className="text-slate-600 text-xs font-mono uppercase flex items-center gap-2">
                <Activity className="w-3 h-3 text-emerald-500" /> System Health
              </h3>
              <span className="text-[10px] text-emerald-600 font-mono font-bold">NOMINAL</span>
            </div>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between text-slate-500">
                <span>Heartbeat</span>
                <span className="text-slate-900">Active (30ms)</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Coevolution</span>
                <span className="text-emerald-600 font-bold">γ {'>'} β</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Observer</span>
                <span className="text-purple-600">Monitoring</span>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur border border-slate-200 p-4 rounded-xl shadow-sm">
            <h3 className="text-slate-600 text-xs font-mono uppercase mb-3">Sectors</h3>
            <div className="space-y-2">
              {Object.entries(SECTOR_COLORS).map(([sector, color]) => (
                <div key={sector} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full border border-black/5 bg-sector-${sector}`} />
                  <span className="text-slate-600 text-xs capitalize">{sector}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer / Selected Node Info */}
      <div className="flex justify-between items-end pointer-events-auto">
        <div className="bg-white/80 backdrop-blur border border-slate-200 p-6 rounded-xl w-96 max-h-[500px] overflow-y-auto shadow-lg">
          {selectedNode ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                  <Box className="w-5 h-5 text-emerald-600" />
                  {selectedNode.label}
                </h2>
                <button onClick={onClose} className="text-slate-400 hover:text-slate-900">×</button>
              </div>

              <div className="text-slate-600 text-sm italic border-l-2 border-emerald-500/30 pl-3">
                {selectedNode.description || "No description available."}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <div className="text-slate-400 text-xs font-mono mb-1">COORDINATES</div>
                  <div className="text-slate-900 font-mono">
                    [{selectedNode.x}, {selectedNode.y}, {selectedNode.z}]
                  </div>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <div className="text-slate-400 text-xs font-mono mb-1">STATUS</div>
                  <div className={`text-slate-900 font-mono capitalize font-bold text-status-${selectedNode.status}`}>
                    {selectedNode.status}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-slate-600 text-sm">
                  <Layers className="w-4 h-4" />
                  <span>Layer: <span className="text-slate-900 uppercase text-xs font-bold bg-slate-100 px-1 rounded border border-slate-200">{selectedNode.layer}</span></span>
                </div>
                <div className="flex items-center gap-2 text-slate-600 text-sm">
                  <Activity className="w-4 h-4" />
                  <span>Sector: <span className={`capitalize font-bold text-sector-${selectedNode.sector}`}>{selectedNode.sector}</span></span>
                </div>
                {selectedNode.agentRole && (
                  <div className="flex items-center gap-2 text-slate-600 text-sm">
                    <Zap className="w-4 h-4 text-amber-500" />
                    <span>Agent Role: <span className="text-amber-600 font-bold">{selectedNode.agentRole}</span></span>
                  </div>
                )}
              </div>

              {selectedNode.capability && (
                <div className="pt-4 border-t border-slate-100">
                  <div className="text-slate-400 text-xs font-mono mb-2">CAPABILITIES / SOURCE</div>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-700 font-mono border border-slate-200">
                      {selectedNode.capability}
                    </span>
                  </div>
                </div>
              )}

              <div className="pt-2">
                <div className="text-slate-400 text-xs font-mono mb-2">MANIFEST</div>
                <div className="bg-slate-900 p-2 rounded text-[10px] font-mono text-emerald-400 overflow-x-auto">
                  {`{
  "id": "${selectedNode.id}",
  "sector": "${selectedNode.sector}",
  "layer": "${selectedNode.layer}"
}`}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Info className="w-8 h-8 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-400 text-sm">Select a node to inspect manifest</p>
            </div>
          )}
        </div>

        <div className="text-right text-slate-400 text-xs font-mono">
          EVOGRID-17 SYSTEM<br />
          GEOMETRY {'>'} TOPOLOGY<br />
          Z-LEVELS: 17
        </div>
      </div>
    </div>
  );
}
