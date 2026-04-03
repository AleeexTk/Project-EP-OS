import React, { useEffect, useState } from 'react';
import { Clock, Activity, Zap, ShieldCheck, MessageSquare } from 'lucide-react';
import { CORE_API_BASE } from '../lib/config';

interface TimelineEvent {
  time: string;
  topic: string;
  module_id: string;
  status?: string;
  payload?: any;
}

const TOPIC_ICONS: Record<string, React.ReactNode> = {
  EXECUTE_TASK: <Zap className="w-4 h-4 text-amber-400" />,
  TASK_RESULT: <ShieldCheck className="w-4 h-4 text-emerald-400" />,
  PROMPT_DISPATCH: <MessageSquare className="w-4 h-4 text-blue-400" />,
  DEFAULT: <Activity className="w-4 h-4 text-slate-400" />
};

export default function TimelinePanel() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTimeline = async () => {
    try {
      const resp = await fetch(`${CORE_API_BASE}/api/timeline?limit=30`);
      if (resp.ok) {
        const data = await resp.json();
        setEvents(data);
      }
    } catch (err) {
      console.error('Failed to fetch timeline:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
    const interval = setInterval(fetchTimeline, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && events.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400 font-mono text-sm">
        <Clock className="w-5 h-5 animate-spin mr-2" />
        LOADING TEMPORAL LOGS...
      </div>
    );
  }

  return (
    <div className="h-full pt-24 pb-6 px-3 md:px-6 max-w-4xl mx-auto flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-3">
          <Clock className="w-6 h-6 text-amber-500" />
          Project Timeline
          <span className="text-[10px] font-mono bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded border border-amber-500/20 uppercase tracking-widest">Live</span>
        </h2>
        <div className="text-[10px] font-mono text-slate-500 uppercase tracking-tighter">
          NDJSON Stream / {events.length} Events Cache
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        {events.length === 0 ? (
          <div className="h-40 flex flex-col items-center justify-center border border-dashed border-white/5 rounded-2xl bg-white/[0.02]">
            <Activity className="w-8 h-8 text-slate-700 mb-2" />
            <p className="text-slate-500 font-mono text-xs">No events registered yet.</p>
            <p className="text-slate-600 font-mono text-[10px] mt-1 italic">Execute a task to see it here.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {events.map((event, idx) => {
              const icon = TOPIC_ICONS[event.topic] || TOPIC_ICONS.DEFAULT;
              const date = new Date(event.time);
              const timeStr = date.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
              
              return (
                <div 
                  key={`${event.time}-${idx}`}
                  className="group relative flex gap-4 p-3 rounded-xl border border-white/5 bg-slate-900/40 hover:bg-slate-800/60 transition-all animate-in fade-in slide-in-from-right-4"
                >
                  <div className="flex-shrink-0 mt-1">
                    {icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[11px] font-bold text-slate-200 tracking-tight">
                        {event.topic}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500 italic">
                        {timeStr}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                       <span className="text-[10px] font-mono text-amber-500/80">@ {event.module_id}</span>
                       {event.status && (
                         <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                           event.status === 'ACCEPTED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                           event.status === 'REJECTED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                           'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                         }`}>
                           {event.status}
                         </span>
                       )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      
      <div className="mt-4 p-4 rounded-xl bg-blue-900/10 border border-blue-500/20">
        <h3 className="text-[11px] font-bold text-blue-400 uppercase mb-2">System Memory Note</h3>
        <p className="text-[11px] text-slate-400 leading-relaxed italic">
          This timeline represents the absolute sequence of events processed by the Temporal Dispatcher. 
          Events are logged post-validation, ensuring the record only contains system-sanctioned activities.
        </p>
      </div>
    </div>
  );
}
