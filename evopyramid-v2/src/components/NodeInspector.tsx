import React from 'react';
import { Bot, ChevronRight, FolderTree, Wrench, X } from 'lucide-react';
import { EvoNode } from '../lib/evo';
import { AgentSession } from '../lib/useSessionRegistry';

interface NodeInspectorProps {
  node: EvoNode;
  sessions: AgentSession[];
  onClose: () => void;
  onActivateAgent: () => void;
  onManifest: () => void;
  onOpenAssistant: () => void;
}

const slugLabel = (value: string) => value.replace(/[^a-zA-Z0-9_-]+/g, '_').replace(/^_+|_+$/g, '') || 'node';
const normalizePath = (value: string) => value.replace(/\\/g, '/');

const getProjectPathForNode = (node: EvoNode) => {
  const pathFromMetadata = node.metadata?.path;
  if (typeof pathFromMetadata === 'string' && pathFromMetadata.trim().length > 0) {
    return normalizePath(pathFromMetadata);
  }
  const layerFolder = node.z >= 11 ? 'α_Pyramid_Core' : node.z >= 5 ? 'β_Pyramid_Functional' : 'γ_Pyramid_Reflective';
  return `${layerFolder}/${node.sector.toUpperCase()}/${node.z}_${slugLabel(node.label ?? node.id)}`;
};

export default function NodeInspector({
  node,
  sessions,
  onClose,
  onActivateAgent,
  onManifest,
  onOpenAssistant,
}: NodeInspectorProps) {
  return (
    <section className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 w-[92%] max-w-lg rounded-2xl bg-slate-900/90 border border-white/10 backdrop-blur p-4 shadow-2xl">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="font-semibold text-sm">{node.label}</h2>
          <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{node.description ?? 'No summary'}</p>
        </div>
        <button
          onClick={onClose}
          title="Deselect node"
          className="p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-white/10"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="mt-3 grid gap-2">
        <div className="flex items-center gap-2 text-[10px] text-slate-400">
          <span>Z{node.z}</span>
          <span>•</span>
          <span>{node.sector.toUpperCase()}</span>
          <span>•</span>
          <span>{node.kind}</span>
        </div>
        <div className="flex items-center gap-2 text-[10px] text-slate-400">
          <FolderTree className="w-3.5 h-3.5 text-emerald-400" />
          <span className="truncate">{getProjectPathForNode(node)}</span>
        </div>

        {/* SK Engine Metrics */}
        <div className="flex items-center gap-3 text-[9px] font-mono">
          <div className="flex items-center gap-1">
            <span className="text-slate-500 uppercase">Memory Color:</span>
            <div 
              className="w-2 h-2 rounded-full shadow-[0_0_5px_rgba(255,255,255,0.3)]" 
              style={{ backgroundColor: node.memory_color || 'white' }}
            />
            <span style={{ color: node.memory_color || 'white' }}>{node.memory_color || 'WHITE'}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-slate-500 uppercase">Gravity:</span>
            <span className="text-emerald-400">{(node.gravity || 1.0).toFixed(2)}</span>
          </div>
        </div>
        {sessions.length > 0 && (
          <div className="flex flex-wrap gap-1.5 text-[10px]">
            {sessions.slice(0, 4).map((session) => (
              <span
                key={session.id}
                className="px-2 py-0.5 rounded-full border border-white/10 bg-white/5 text-slate-300"
              >
                {session.provider.toUpperCase()} • {session.status}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          onClick={onActivateAgent}
          className="flex-1 min-w-[140px] px-3 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-semibold flex items-center justify-center gap-1.5"
        >
          <Bot className="w-3.5 h-3.5" />
          Activate Agent
        </button>
        <button
          onClick={onManifest}
          className="px-3 py-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-[11px] font-semibold flex items-center gap-1.5 border border-amber-500/30"
        >
          <Wrench className="w-3.5 h-3.5" />
          Manifest Node
        </button>
        <button
          onClick={onOpenAssistant}
          className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-[11px] font-semibold flex items-center gap-1.5"
        >
          Open Assistant
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </section>
  );
}
