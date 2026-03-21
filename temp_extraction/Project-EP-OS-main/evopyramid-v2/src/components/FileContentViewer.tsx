import React, { useState, useEffect } from 'react';
import { X, Save, FileCode, Loader2, Zap } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';

interface FileContentViewerProps {
  path: string | null;
  onClose: () => void;
  onInject?: (content: string) => void;
}

export default function FileContentViewer({ path, onClose, onInject }: FileContentViewerProps) {
  const [content, setContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState<string | null>(null);

  useEffect(() => {
    if (!path) return;
    
    const loadFile = async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await fetch(`${CORE_API_BASE}/v1/workspace/file?path=${encodeURIComponent(path)}`);
        if (!resp.ok) throw new Error(`Status ${resp.status}`);
        const data = await resp.json();
        setContent(data.content);
        setEditedContent(data.content);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    loadFile();
  }, [path]);

  const handleCommit = async () => {
    if (!path || editedContent === null) return;
    setLoading(true);
    try {
      const resp = await fetch(`${CORE_API_BASE}/v1/workspace/commit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content: editedContent, overwrite: true })
      });
      if (!resp.ok) throw new Error(`Commit failed: ${resp.status}`);
      setContent(editedContent);
      setIsEditing(false);
      // We could use a custom Modal here, but alert is fine for now
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (!path) return null;

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-white/10 rounded-lg shadow-xl overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 bg-black/40 border-b border-white/10">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-mono text-slate-300 truncate max-w-[200px]">{path.split('/').pop()}</span>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-white/10 rounded" title="Close File Details">
          <X className="w-4 h-4 text-slate-500" />
        </button>
      </div>
      
      <div className="flex-1 overflow-auto p-4 custom-scrollbar bg-slate-950 font-mono text-[11px] leading-relaxed">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-40 gap-2">
            <Loader2 className="w-5 h-5 text-emerald-500 animate-spin" />
            <span className="text-slate-500">Processing...</span>
          </div>
        ) : error ? (
          <div className="text-rose-400 p-4 border border-rose-500/20 bg-rose-500/5 rounded">Error: {error}</div>
        ) : isEditing ? (
          <textarea 
            className="w-full h-full bg-transparent text-slate-300 outline-none resize-none"
            value={editedContent || ''}
            onChange={(e) => setEditedContent(e.target.value)}
            title="File Editor"
            placeholder="Enter code here..."
          />
        ) : (
          <pre className="text-slate-300 whitespace-pre-wrap">
            {content}
          </pre>
        )}
      </div>
      
      {!loading && (
        <div className="p-2 border-t border-white/5 bg-black/20 flex gap-2 justify-end shrink-0">
          <div className="text-[9px] text-slate-600 mr-auto px-2 uppercase tracking-tighter self-center">
            {isEditing ? 'Staging Changes' : 'Inspect Mode'}
          </div>
          
          {onInject && !isEditing && (
            <button 
              onClick={() => onInject(`FILE: ${path}\n\`\`\`\n${content}\n\`\`\``)}
              className="flex items-center gap-1.5 px-3 py-1 bg-blue-600/20 border border-blue-500/30 text-blue-400 text-[10px] rounded hover:bg-blue-600/30 transition-colors uppercase font-bold"
              title="Inject into Z-Bus prompt"
            >
              <Zap className="w-3 h-3" /> Inject context
            </button>
          )}

          {isEditing ? (
            <>
              <button 
                onClick={() => { setIsEditing(false); setEditedContent(content); }}
                className="px-3 py-1 text-slate-400 text-[10px] uppercase font-bold hover:text-slate-200"
              >
                Discard
              </button>
              <button 
                onClick={handleCommit}
                className="flex items-center gap-1.5 px-3 py-1 bg-emerald-600 border border-emerald-500 text-white text-[10px] rounded hover:bg-emerald-500 transition-colors uppercase font-bold shadow-[0_0_10px_rgba(16,185,129,0.3)]"
              >
                <Save className="w-3 h-3" /> Commit & Push
              </button>
            </>
          ) : (
            <button 
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-1.5 px-3 py-1 bg-emerald-600/20 border border-emerald-500/30 text-emerald-400 text-[10px] rounded hover:bg-emerald-600/30 transition-colors uppercase font-bold"
            >
              <FileCode className="w-3 h-3" /> Edit File
            </button>
          )}
        </div>
      )}
    </div>
  );
}
