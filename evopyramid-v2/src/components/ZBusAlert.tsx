import React from 'react';
import { Activity } from 'lucide-react';

interface ZBusAlertProps {
  event: any;
}

const ZBusAlert: React.FC<ZBusAlertProps> = ({ event }) => {
  if (!event) return null;

  return (
    <div className={`absolute top-[200px] left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-[650px] border rounded-lg p-3 text-[11px] flex flex-col items-start gap-1 backdrop-blur shadow-2xl transition-colors duration-500
      ${event.status === 'degraded' ? 'bg-amber-950/90 border-amber-500/60' : 
        event.status === 'failed' ? 'bg-rose-950/90 border-rose-500/60' : 
        'bg-emerald-950/90 border-emerald-500/60'}`}
    >
      <div className={`flex items-start md:items-center gap-3 w-full
        ${event.status === 'degraded' ? 'text-amber-200' : 
          event.status === 'failed' ? 'text-rose-200' : 
          'text-emerald-200'}`}
      >
        <Activity className="w-4 h-4 shrink-0 mt-0.5 md:mt-0" />
        <div className="flex flex-col w-full">
          <div className="flex justify-between items-center w-full">
            <span className="font-bold tracking-wider">
              {event.event_type} {event.simulation ? '(SIMULATION)' : ''}
            </span>
            <span className="opacity-70 text-[9px]">{event.node_id}</span>
          </div>
          <span className="opacity-90 mt-1">
            {event.event_type === 'NODE_FALLBACK_INIT' && `Provider ${event.provider} timeout. Falling back to ${event.fallback_to}.`}
            {event.event_type === 'PROVIDER_TIMEOUT' && `Provider ${event.provider} timed out. Task: ${event.payload?.task}`}
            {event.event_type === 'NODE_RECOVERY_SUCCESS' && `Resolved with ${event.provider}. Status: ${event.payload?.result}`}
            {event.event_type === 'NODE_START' && `Starting task: ${event.payload?.task}`}
            {event.event_type === 'PROVIDER_SELECTED' && `Selected provider: ${event.provider}`}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ZBusAlert;
