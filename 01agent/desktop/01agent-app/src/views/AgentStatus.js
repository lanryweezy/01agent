import React, { useState, useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import {
  Search,
  Activity,
  Terminal,
  ShieldCheck,
  Zap,
  Trash2,
  Download,
  Filter,
  Play,
  Square,
  RefreshCw,
  Cpu,
  Database,
  Globe,
  CheckCircle2,
  AlertCircle,
  Info
} from 'lucide-react';

const AgentStatus = () => {
  const [agentStatus, setAgentStatus] = useState({
    isRunning: false,
    currentTask: null,
    strategy: 'speed_priority',
    uptime: 0,
    tasksCompleted: 0,
    tasksInQueue: 0,
    systemHealth: { cpu: 0, memory: 0, disk: 0, network: 0 },
    components: {
      smartExecutor: 'active',
      terminalController: 'active',
      backgroundExecutor: 'active',
      fastUIDetector: 'active',
      performanceOptimizer: 'active',
      configManager: 'active'
    },
    logs: []
  });

  const [selectedLogLevel, setSelectedLogLevel] = useState('all');

  useEffect(() => {
    if (window.electronAPI?.onAIAgentLaunch) {
      window.electronAPI.onAIAgentLaunch((threadId) => {
        setAgentStatus(prev => ({
          ...prev,
          isRunning: true,
          currentTask: `Thread ${threadId}`,
          uptime: 0
        }));
        addLog('info', `Agent initialized for thread sequence ${threadId}`);
      });
    }

    if (window.electronAPI?.onAIAgentExit) {
      window.electronAPI.onAIAgentExit(() => {
        setAgentStatus(prev => ({ ...prev, isRunning: false, currentTask: null }));
        addLog('info', 'Agent execution lifecycle terminated');
      });
    }

    const interval = setInterval(() => {
      setAgentStatus(prev => ({
        ...prev,
        uptime: prev.isRunning ? prev.uptime + 2 : 0,
        tasksCompleted: prev.isRunning ? prev.tasksCompleted + (Math.random() < 0.1 ? 1 : 0) : prev.tasksCompleted,
        tasksInQueue: Math.floor(Math.random() * 3),
        systemHealth: {
          cpu: 10 + Math.random() * 30,
          memory: 40 + Math.random() * 20,
          disk: 15,
          network: Math.random() * 5
        }
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const addLog = (level, message) => {
    const newLog = { id: Date.now(), timestamp: new Date(), level, message };
    setAgentStatus(prev => ({ ...prev, logs: [...prev.logs.slice(-199), newLog] }));
  };

  const startAgent = () => {
    if (window.electronAPI?.launchAIAgent) {
      const baseURL = process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS;
      window.electronAPI.launchAIAgent(baseURL, 'system-monitor', false);
    }
  };

  const stopAgent = () => window.electronAPI?.stopAIAgent?.();

  const formatUptime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  };

  // ⚡ Bolt: Memoized System Vitals mapping to prevent VDOM recreation during unconnected telemetry updates
  const memoizedSystemVitals = useMemo(() => (
    [
      { name: 'CPU', val: agentStatus.systemHealth.cpu, icon: Cpu, color: 'bg-emerald-500' },
      { name: 'RAM', val: agentStatus.systemHealth.memory, icon: Database, color: 'bg-cyan-500' },
      { name: 'NET', val: agentStatus.systemHealth.network, icon: Globe, color: 'bg-indigo-500' }
    ].map(m => (
      <div key={m.name}>
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-medium text-slate-400 flex items-center gap-2">
            <m.icon className="w-3.5 h-3.5" /> {m.name}
          </span>
          <span className="text-xs font-mono text-white font-bold">{m.val.toFixed(1)}%</span>
        </div>
        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
          <div className={`h-full ${m.color} transition-all duration-1000`} style={{ width: `${m.val}%` }} />
        </div>
      </div>
    ))
  ), [agentStatus.systemHealth.cpu, agentStatus.systemHealth.memory, agentStatus.systemHealth.network]);

  // ⚡ Bolt: Memoized Core Orchestrator Matrix mapping to prevent VDOM recreation on unconnected state changes
  const memoizedCoreMatrix = useMemo(() => (
    Object.entries(agentStatus.components).map(([name, status]) => (
      <div key={name} className="bg-white/[0.02] border border-white/5 rounded-xl p-4 flex flex-col items-center text-center group hover:bg-white/[0.04] transition-all">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-[10px] font-bold text-slate-300 uppercase tracking-tighter leading-tight">
          {name.replace(/([A-Z])/g, ' $1').trim()}
        </div>
        <div className="text-[9px] text-emerald-500/70 mt-1 font-mono">{status.toUpperCase()}</div>
      </div>
    ))
  ), [agentStatus.components]);

  const memoizedLogElements = useMemo(() => {
    const filteredLogs = agentStatus.logs.filter(log => selectedLogLevel === 'all' || log.level === selectedLogLevel);

    if (filteredLogs.length === 0) {
      return <div className="text-center py-12 text-slate-500 italic text-sm">No diagnostic events recorded in current buffer</div>;
    }

    return filteredLogs.map(log => (
      <div key={log.id} className="group flex gap-4 py-2 px-3 hover:bg-white/[0.02] transition-colors border-b border-white/5 last:border-0 font-mono text-[11px]">
        <span className="text-slate-500 whitespace-nowrap">{log.timestamp.toLocaleTimeString()}</span>
        <span className={`font-bold uppercase w-16 ${
          log.level === 'error' ? 'text-rose-400' :
          log.level === 'warning' ? 'text-amber-400' : 'text-cyan-400'
        }`}>{log.level}</span>
        <span className="text-slate-300 flex-1">{log.message}</span>
      </div>
    ));
  }, [agentStatus.logs, selectedLogLevel]);

  return (
    <div className="flex-1 h-full flex flex-col bg-[#0a0f1d] overflow-hidden">
      {/* Header */}
      <header className="px-8 py-6 border-b border-white/10 flex items-center justify-between bg-white/[0.02] backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 flex items-center justify-center border border-cyan-500/20">
            <Search className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Agent Diagnostic</h1>
            <p className="text-slate-400 text-sm flex items-center gap-2">
              Status:
              <span className={`inline-flex items-center gap-1.5 font-bold uppercase tracking-tighter ${agentStatus.isRunning ? 'text-emerald-400' : 'text-slate-500'}`}>
                <div className={`w-2 h-2 rounded-full ${agentStatus.isRunning ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
                {agentStatus.isRunning ? 'Operational' : 'Standby'}
              </span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {!agentStatus.isRunning ? (
            <button onClick={startAgent} className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-900 px-6 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-emerald-500/20">
              <Play className="w-4 h-4 fill-current" /> Initialize Agent
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button onClick={() => window.location.reload()} className="p-2.5 rounded-xl bg-white/5 text-slate-400 hover:text-white transition-colors">
                <RefreshCw className="w-5 h-5" />
              </button>
              <button onClick={stopAgent} className="flex items-center gap-2 bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 px-6 py-2.5 rounded-xl font-bold border border-rose-500/30 transition-all">
                <Square className="w-4 h-4 fill-current" /> Terminate Instance
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          
          {/* Quick Stats */}
          <div className="xl:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Runtime Uptime', value: formatUptime(agentStatus.uptime), icon: Activity, color: 'text-cyan-400' },
              { label: 'Active Task', value: agentStatus.currentTask || 'N/A', icon: Terminal, color: 'text-emerald-400' },
              { label: 'Exec Strategy', value: 'Vision V2', icon: Zap, color: 'text-amber-400' },
              { label: 'Queue Depth', value: agentStatus.tasksInQueue, icon: ShieldCheck, color: 'text-indigo-400' }
            ].map((stat, i) => (
              <div key={i} className="bg-white/[0.03] border border-white/5 rounded-2xl p-5 backdrop-blur-sm">
                <stat.icon className={`w-5 h-5 ${stat.color} mb-3`} />
                <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">{stat.label}</div>
                <div className="text-lg font-bold text-white mt-1 truncate">{stat.value}</div>
              </div>
            ))}
          </div>

          {/* System Health */}
          <div className="bg-white/[0.03] border border-white/5 rounded-2xl p-6 backdrop-blur-sm">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
              <Activity className="w-4 h-4" /> System Vitals
            </h3>
            <div className="space-y-5">
              {memoizedSystemVitals}
            </div>
          </div>
        </div>

        {/* Component Health Grid */}
        <section>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.2em] mb-4">Core Orchestrator Matrix</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {memoizedCoreMatrix}
          </div>
        </section>

        {/* Logs */}
        <section className="bg-black/40 border border-white/10 rounded-2xl flex flex-col overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-white/5">
            <div className="flex items-center gap-3">
              <Terminal className="w-5 h-5 text-cyan-400" />
              <h3 className="font-bold text-white text-sm uppercase tracking-wider">Live System Events</h3>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center bg-black/40 border border-white/10 rounded-lg px-2">
                <Filter className="w-3.5 h-3.5 text-slate-500 mr-2" />
                <select
                  value={selectedLogLevel}
                  onChange={(e) => setSelectedLogLevel(e.target.value)}
                  className="bg-transparent border-none text-[11px] text-slate-300 focus:ring-0 py-1.5"
                >
                  <option value="all">ALL LEVELS</option>
                  <option value="info">INFO</option>
                  <option value="warning">WARNING</option>
                  <option value="error">ERROR</option>
                </select>
              </div>
              <div className="h-4 w-px bg-white/10" />
              <button onClick={() => setAgentStatus(p => ({...p, logs: []}))} className="text-slate-500 hover:text-rose-400 transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
              <button className="text-slate-500 hover:text-cyan-400 transition-colors">
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="h-[400px] overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 p-2">
            {memoizedLogElements}
          </div>

          <div className="px-6 py-3 bg-white/5 border-t border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
              <Info className="w-3 h-3" />
              LOG_BUFFER_SIZE: {agentStatus.logs.length} / 200
            </div>
            <div className="text-[10px] text-slate-600 font-mono italic">
              * Showing {selectedLogLevel.toUpperCase()} events
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AgentStatus;
