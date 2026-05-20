import React, { useState, useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import {
  Activity,
  Cpu,
  Database,
  BarChart3,
  Zap,
  Clock,
  RefreshCw,
  Download,
  Trash2,
  Play,
  Pause,
  ChevronRight,
  ShieldCheck,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie
} from 'recharts';

const MetricCard = ({ title, value, unit, icon: Icon, colorClass }) => (
  <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-5 backdrop-blur-sm group hover:border-white/20 transition-all">
    <div className="flex items-center gap-2 mb-4">
      <Icon className={`w-4 h-4 ${colorClass}`} />
      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{title}</span>
    </div>
    <div className="flex items-baseline gap-1">
      <span className="text-2xl font-black text-white">{value}</span>
      <span className="text-xs text-slate-500 font-bold">{unit}</span>
    </div>
  </div>
);

const Performance = () => {
  const isDarkMode = useSelector(state => state.isDarkMode);
  
  const [performanceData, setPerformanceData] = useState({
    realTime: {
      cpu: 24.5,
      memory: 4.2,
      tasks: 12,
      successRate: 94.2,
      avgExecutionTime: 1.45,
      status: 'working'
    },
    methods: [
      { name: 'Terminal', count: 85, success: 98, color: '#10b981' },
      { name: 'GUI', count: 42, success: 85, color: '#06b6d4' },
      { name: 'Background', count: 28, success: 92, color: '#6366f1' },
      { name: 'Smart', count: 64, success: 95, color: '#f59e0b' }
    ],
    history: [
      { time: '12:00', cpu: 20, mem: 35, tasks: 5 },
      { time: '12:10', cpu: 45, mem: 40, tasks: 8 },
      { time: '12:20', cpu: 30, mem: 45, tasks: 12 },
      { time: '12:30', cpu: 65, mem: 50, tasks: 15 },
      { time: '12:40', cpu: 40, mem: 48, tasks: 10 },
      { time: '12:50', cpu: 25, mem: 45, tasks: 12 },
    ],
    executionStream: [
      { time: '12:50:01', action: 'Capture Screenshot', status: 'success' },
      { time: '12:50:05', action: 'Vision Reasoning', status: 'success' },
      { time: '12:50:08', action: 'Execute: Click Button', status: 'working' },
    ]
  });

  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        setPerformanceData(prev => ({
          ...prev,
          realTime: {
            ...prev.realTime,
            cpu: 15 + Math.random() * 40,
            memory: 4.0 + Math.random() * 0.5,
          },
          history: [...prev.history.slice(1), {
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            cpu: 15 + Math.random() * 40,
            mem: 35 + Math.random() * 20,
            tasks: Math.floor(Math.random() * 20)
          }]
        }));
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const memoizedHistoryChart = useMemo(() => (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={performanceData.history}>
        <defs>
          <linearGradient id="perfCpu" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="perfMem" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
        <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
        <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }}
          itemStyle={{ fontSize: '12px' }}
        />
        <Area type="monotone" dataKey="cpu" stroke="#10b981" fill="url(#perfCpu)" strokeWidth={2} />
        <Area type="monotone" dataKey="mem" stroke="#06b6d4" fill="url(#perfMem)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  ), [performanceData.history]);

  return (
    <div className="flex-1 h-full flex flex-col bg-[#0a0f1d] overflow-hidden text-slate-200">
      {/* Header */}
      <header className="px-8 py-6 border-b border-white/5 flex items-center justify-between bg-white/[0.02] backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
            <BarChart3 className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">Performance Analytics</h1>
            <div className="flex items-center gap-2 mt-0.5">
              <TrendingUp className="w-3 h-3 text-emerald-400" />
              <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Efficiency Optimized</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all border ${
              autoRefresh
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'bg-white/5 border-white/10 text-slate-400'
            }`}
          >
            {autoRefresh ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            {autoRefresh ? 'LIVE STREAM' : 'PAUSED'}
          </button>
          <button className="p-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-slate-400 transition-colors">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-thin scrollbar-thumb-white/10">

        {/* Metric Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <MetricCard title="CPU Utilization" value={performanceData.realTime.cpu.toFixed(1)} unit="%" icon={Cpu} colorClass="text-emerald-400" />
          <MetricCard title="Active Memory" value={performanceData.realTime.memory.toFixed(1)} unit="GB" icon={Database} colorClass="text-cyan-400" />
          <MetricCard title="Task Success" value={performanceData.realTime.successRate} unit="%" icon={ShieldCheck} colorClass="text-indigo-400" />
          <MetricCard title="Throughput" value={performanceData.realTime.tasks} unit="ops/m" icon={Zap} colorClass="text-amber-400" />
          <MetricCard title="Avg Latency" value={performanceData.realTime.avgExecutionTime} unit="s" icon={Clock} colorClass="text-rose-400" />
        </div>

        {/* Main Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
           {/* Real-time Load Chart */}
           <div className="lg:col-span-2 bg-white/[0.03] border border-white/5 rounded-3xl p-6 backdrop-blur-sm">
             <div className="flex items-center justify-between mb-8">
               <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                 <Activity className="w-4 h-4 text-emerald-400" /> System Load History
               </h3>
               <div className="flex gap-4">
                 <div className="flex items-center gap-2 text-[10px] font-bold text-emerald-400/80">
                   <div className="w-2 h-2 rounded-full bg-emerald-500" /> CPU
                 </div>
                 <div className="flex items-center gap-2 text-[10px] font-bold text-cyan-400/80">
                   <div className="w-2 h-2 rounded-full bg-cyan-500" /> RAM
                 </div>
               </div>
             </div>
             <div className="h-[300px] w-full">
               {memoizedHistoryChart}
             </div>
           </div>

           {/* Execution Methods Bar Chart */}
           <div className="bg-white/[0.03] border border-white/5 rounded-3xl p-6 backdrop-blur-sm flex flex-col">
             <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 mb-8">
               <Zap className="w-4 h-4 text-amber-400" /> Execution Stratagem
             </h3>
             <div className="flex-1 flex flex-col justify-between">
                {performanceData.methods.map((method, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex justify-between items-center text-[11px] font-bold">
                      <span className="text-slate-300">{method.name.toUpperCase()}</span>
                      <span className="text-white">{method.success}% SUCCESS</span>
                    </div>
                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-1000"
                        style={{ width: `${method.success}%`, backgroundColor: method.color }}
                      />
                    </div>
                    <div className="text-[9px] text-slate-500 text-right uppercase">{method.count} tasks executed</div>
                  </div>
                ))}
             </div>
             <div className="mt-8 pt-6 border-t border-white/5">
                <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-3 flex items-start gap-3">
                  <AlertCircle className="w-4 h-4 text-emerald-400 mt-0.5" />
                  <p className="text-[10px] leading-relaxed text-emerald-400/70 italic">
                    "Switching to terminal-centric execution for high-frequency tasks recommended."
                  </p>
                </div>
             </div>
           </div>
        </div>

        {/* Action Stream */}
        <section className="bg-black/40 border border-white/10 rounded-3xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-white/5">
            <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" /> Live Execution Stream
            </h3>
            <div className="flex gap-2">
              <button className="p-1.5 text-slate-500 hover:text-white transition-colors"><Download className="w-4 h-4" /></button>
              <button className="p-1.5 text-slate-500 hover:text-rose-400 transition-colors"><Trash2 className="w-4 h-4" /></button>
            </div>
          </div>
          <div className="max-h-[300px] overflow-y-auto p-4 space-y-1">
            {performanceData.executionStream.map((log, i) => (
              <div key={i} className="flex items-center gap-4 py-2 px-3 hover:bg-white/[0.02] rounded-lg transition-colors font-mono text-[11px]">
                <span className="text-slate-500">{log.time}</span>
                <ChevronRight className="w-3 h-3 text-emerald-500" />
                <span className="text-slate-300 flex-1">{log.action}</span>
                <span className={`px-2 py-0.5 rounded uppercase font-bold text-[9px] ${
                  log.status === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400 animate-pulse'
                }`}>
                  {log.status}
                </span>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
};

export default Performance;
