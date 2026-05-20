import React from 'react';
import {
  Play,
  Activity,
  Settings,
  ExternalLink,
  Camera,
  Zap,
  Terminal,
  Cpu,
  Server,
  LayoutDashboard
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const mockChartData = [
  { time: '10:00', load: 32 },
  { time: '10:05', load: 45 },
  { time: '10:10', load: 28 },
  { time: '10:15', load: 55 },
  { time: '10:20', load: 42 },
  { time: '10:25', load: 38 },
  { time: '10:30', load: 48 },
];

const StatCard = ({ title, icon: Icon, children, className = "" }) => (
  <div className={`bg-white/[0.03] border border-white/10 rounded-2xl p-6 backdrop-blur-xl hover:border-emerald-500/30 transition-all group ${className}`}>
    <div className="flex items-center gap-3 mb-4">
      <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 group-hover:bg-emerald-500/20 transition-colors">
        <Icon className="w-5 h-5 text-emerald-400" />
      </div>
      <h3 className="font-bold text-white uppercase tracking-wider text-sm">{title}</h3>
    </div>
    {children}
  </div>
);

const Dashboard = () => {
  return (
    <div className="flex-1 bg-[#0a0f1d] text-slate-200 overflow-y-auto">
      <div className="max-w-7xl mx-auto p-8 space-y-8 animate-in fade-in duration-700">

        {/* Hero Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <LayoutDashboard className="w-8 h-8 text-slate-900" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white tracking-tight">01Agent <span className="text-emerald-400">Elite</span></h1>
              <p className="text-slate-400 font-medium">Command Center • <span className="text-emerald-500/80">v2.2.0 Stable</span></p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-tighter">System Ready</span>
            </div>
            <button className="p-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <Settings className="w-5 h-5 text-slate-400" />
            </button>
          </div>
        </header>

        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          {/* Agent Control */}
          <StatCard title="Agent Orchestrator" icon={Play}>
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Active Instance</div>
                  <div className="text-xl font-mono text-white">#ST-9942</div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Uptime</div>
                  <div className="text-sm font-mono text-emerald-400">02:45:12</div>
                </div>
              </div>
              <button className="w-full py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-900 rounded-xl font-black uppercase tracking-widest text-xs transition-all shadow-lg shadow-emerald-500/20 hover:scale-[1.02] active:scale-[0.98]">
                Initialize AI Agent
              </button>
            </div>
          </StatCard>

          {/* Performance Summary */}
          <StatCard title="Throughput Capacity" icon={Activity} className="lg:col-span-2">
            <div className="h-[120px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockChartData}>
                  <defs>
                    <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #ffffff10', borderRadius: '8px', fontSize: '10px' }}
                    itemStyle={{ color: '#10b981' }}
                  />
                  <Area type="monotone" dataKey="load" stroke="#10b981" fillOpacity={1} fill="url(#colorLoad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </StatCard>

          {/* Vitals Grid */}
          <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span className="text-[10px] font-bold text-slate-500 uppercase">CPU Architecture</span>
              </div>
              <div className="text-2xl font-black text-white">24.8<span className="text-xs text-slate-500 ml-1">%</span></div>
              <div className="w-full h-1 bg-white/5 rounded-full mt-3 overflow-hidden">
                <div className="h-full bg-cyan-500" style={{ width: '24.8%' }} />
              </div>
            </div>

            <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Server className="w-4 h-4 text-amber-400" />
                <span className="text-[10px] font-bold text-slate-500 uppercase">Memory Cluster</span>
              </div>
              <div className="text-2xl font-black text-white">4.2<span className="text-xs text-slate-500 ml-1">GB</span></div>
              <div className="w-full h-1 bg-white/5 rounded-full mt-3 overflow-hidden">
                <div className="h-full bg-amber-500" style={{ width: '42%' }} />
              </div>
            </div>

            <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Terminal className="w-4 h-4 text-emerald-400" />
                <span className="text-[10px] font-bold text-slate-500 uppercase">Task Efficiency</span>
              </div>
              <div className="text-2xl font-black text-white">98.2<span className="text-xs text-slate-500 ml-1">%</span></div>
              <div className="w-full h-1 bg-white/5 rounded-full mt-3 overflow-hidden">
                <div className="h-full bg-emerald-500" style={{ width: '98.2%' }} />
              </div>
            </div>

            <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-4 h-4 text-rose-400" />
                <span className="text-[10px] font-bold text-slate-500 uppercase">Logic Latency</span>
              </div>
              <div className="text-2xl font-black text-white">45<span className="text-xs text-slate-500 ml-1">ms</span></div>
              <div className="w-full h-1 bg-white/5 rounded-full mt-3 overflow-hidden">
                <div className="h-full bg-rose-500" style={{ width: '15%' }} />
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <StatCard title="Automation Matrix" icon={Zap}>
            <div className="grid grid-cols-2 gap-3">
              <button className="flex flex-col items-center justify-center p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-emerald-500/10 hover:border-emerald-500/30 transition-all group">
                <Camera className="w-5 h-5 text-slate-400 group-hover:text-emerald-400 mb-2" />
                <span className="text-[10px] font-bold text-slate-500 group-hover:text-emerald-400 uppercase">Capture</span>
              </button>
              <button className="flex flex-col items-center justify-center p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-cyan-500/10 hover:border-cyan-500/30 transition-all group">
                <Terminal className="w-5 h-5 text-slate-400 group-hover:text-cyan-400 mb-2" />
                <span className="text-[10px] font-bold text-slate-500 group-hover:text-cyan-400 uppercase">Terminal</span>
              </button>
              <button className="flex flex-col items-center justify-center p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-amber-500/10 hover:border-amber-500/30 transition-all group">
                <Activity className="w-5 h-5 text-slate-400 group-hover:text-amber-400 mb-2" />
                <span className="text-[10px] font-bold text-slate-500 group-hover:text-amber-400 uppercase">Observe</span>
              </button>
              <button className="flex flex-col items-center justify-center p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-rose-500/10 hover:border-rose-500/30 transition-all group">
                <Zap className="w-5 h-5 text-slate-400 group-hover:text-rose-400 mb-2" />
                <span className="text-[10px] font-bold text-slate-500 group-hover:text-rose-400 uppercase">Optimize</span>
              </button>
            </div>
          </StatCard>

          {/* Infrastructure */}
          <StatCard title="Infrastructure" icon={Server}>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-black/20 rounded-xl border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-xs font-medium">Backend API</span>
                </div>
                <a href="http://localhost:8001" target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:text-emerald-300">
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
              <div className="flex items-center justify-between p-3 bg-black/20 rounded-xl border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-xs font-medium">Interactive Docs</span>
                </div>
                <a href="http://localhost:8001/docs" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300">
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
              <div className="pt-2 text-center">
                <p className="text-[10px] text-slate-500 font-mono italic">Cluster Connection Stable</p>
              </div>
            </div>
          </StatCard>

          {/* AI Model Intelligence */}
          <StatCard title="AI Intelligence" icon={Cpu}>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Primary Core</span>
                <span className="text-white font-bold">Claude 3.7 Sonnet</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Logic Parser</span>
                <span className="text-white font-bold">GPT-4o</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Vision Mode</span>
                <span className="text-emerald-400 font-bold">Extended Thinking</span>
              </div>
              <div className="mt-4 p-3 bg-emerald-500/5 rounded-xl border border-emerald-500/10 text-[10px] leading-relaxed text-emerald-400/80 italic">
                "Computer Use and high-speed visual reasoning enabled for native OS automation."
              </div>
            </div>
          </StatCard>

        </div>

        <footer className="pt-8 border-t border-white/5 text-center">
          <p className="text-xs text-slate-500 font-medium">© 2025 01Agent Desktop Platform • High-Performance AI Automation</p>
        </footer>
      </div>
    </div>
  );
};

export default Dashboard;
