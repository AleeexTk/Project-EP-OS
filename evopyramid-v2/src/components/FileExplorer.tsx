import React, { useState, useEffect } from 'react';
import { Folder, File, ChevronRight, ChevronDown, RefreshCw, FileText } from 'lucide-react';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size: number;
  children?: FileNode[];
}

interface FileExplorerProps {
  onFileSelect: (path: string) => void;
}

const API_BASE = 'http://localhost:8000'; // Evo API Base

export default function FileExplorer({ onFileSelect }: FileExplorerProps) {
  const [tree, setTree] = useState<FileNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const loadTree = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/v1/workspace/tree`);
      const data = await resp.json();
      setTree(data);
    } catch (e) {
      console.error("Failed to load file tree", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTree();
  }, []);

  const toggleExpand = (path: string) => {
    setExpanded(prev => ({ ...prev, [path]: !prev[path] }));
  };

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expanded[node.path];
    const isDir = node.type === 'directory';

    return (
      <div key={node.path} className="select-none">
        <div 
          className={`flex items-center gap-1 py-1 px-2 cursor-pointer hover:bg-white/5 rounded text-[12px] group ${isDir ? 'text-slate-300' : 'text-slate-400'}`}
          data-depth={depth}
          onClick={() => isDir ? toggleExpand(node.path) : onFileSelect(node.path)}
        >
          {isDir ? (
            isExpanded ? <ChevronDown className="w-3 h-3 text-slate-500" /> : <ChevronRight className="w-3 h-3 text-slate-500" />
          ) : (
            <FileText className="w-3 h-3 text-slate-600 group-hover:text-emerald-500 transition-colors" />
          )}
          {isDir ? <Folder className={`w-3.5 h-3.5 ${isExpanded ? 'text-amber-400/80' : 'text-amber-500/60'}`} /> : null}
          <span className="truncate">{node.name}</span>
        </div>
        
        {isDir && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/50 rounded-lg border border-white/5 overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/5 bg-black/20">
        <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Workspace Tree</span>
        <button onClick={loadTree} className="p-1 hover:bg-white/10 rounded transition-colors" title="Refresh Tree">
          <RefreshCw className={`w-3 h-3 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar p-1">
        {loading && !tree ? (
          <div className="flex items-center justify-center h-20 text-slate-600 animate-pulse text-[11px]">Initializing File Layer...</div>
        ) : (
          tree && renderNode(tree)
        )}
      </div>
    </div>
  );
}
