import React from 'react';
import { Layers3, Radar, Sparkles, Table2 } from 'lucide-react';

type TabId = 'core' | 'nexus' | 'genesis' | 'table';

interface NavigationTabsProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

const NavigationTabs: React.FC<NavigationTabsProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="absolute top-16 left-1/2 -translate-x-1/2 z-40 flex items-center gap-1 p-1 rounded-full bg-black/35 border border-white/10 backdrop-blur-md shadow-2xl">
      <button
        onClick={() => onTabChange('core')}
        className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 transition-all duration-300 ${activeTab === 'core' ? 'bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.4)]' : 'text-slate-300 hover:bg-white/10'}`}
      >
        <Layers3 className="w-3.5 h-3.5" />
        Core
      </button>
      <button
        onClick={() => onTabChange('genesis')}
        className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 transition-all duration-300 ${activeTab === 'genesis' ? 'bg-emerald-600 text-white shadow-[0_0_15px_rgba(5,150,105,0.4)]' : 'text-slate-300 hover:bg-white/10'}`}
      >
        <Sparkles className="w-3.5 h-3.5" />
        Genesis
      </button>
      <button
        onClick={() => onTabChange('nexus')}
        className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 transition-all duration-300 ${activeTab === 'nexus' ? 'bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)]' : 'text-slate-300 hover:bg-white/10'}`}
      >
        <Radar className="w-3.5 h-3.5" />
        Nexus
      </button>
      <button
        onClick={() => onTabChange('table')}
        className={`px-3 py-1.5 rounded-full text-[11px] font-semibold flex items-center gap-1.5 transition-all duration-300 ${activeTab === 'table' ? 'bg-violet-600 text-white shadow-[0_0_15px_rgba(124,58,237,0.4)]' : 'text-slate-300 hover:bg-white/10'}`}
      >
        <Table2 className="w-3.5 h-3.5" />
        Table
      </button>
    </div>
  );
};

export default NavigationTabs;
