import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  Home,
  MessageSquare,
  BarChart3,
  Search,
  Settings,
  Moon,
  Sun,
  Play,
  Square,
  RefreshCw,
  Zap,
  Cpu,
  Brain,
  Rocket,
  Activity,
  User as UserIcon,
  LayoutDashboard
} from 'lucide-react';
import { setDarkMode } from '../store';

const NavItem = ({ icon: Icon, label, path, active, onClick, status }) => (
  <button
    onClick={() => onClick(path)}
    className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group ${
      active
        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-lg shadow-emerald-500/5'
        : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent'
    }`}
  >
    <div className="flex items-center gap-3">
      <Icon className={`w-5 h-5 ${active ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-300'} transition-colors`} />
      <span className="text-sm font-bold uppercase tracking-wider">{label}</span>
    </div>
    {status === 'working' && active && (
      <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
    )}
  </button>
);

const ModernSidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  
  const isDarkMode = useSelector(state => state.isDarkMode);
  const user = useSelector(state => state.user);
  
  const [agentStatus, setAgentStatus] = useState('idle');
  const [performanceData, setPerformanceData] = useState({
    cpu: 24.8,
    memory: 42.1,
    tasks: 12,
    successRate: 98.2
  });
  const [isAgentRunning, setIsAgentRunning] = useState(false);

  useEffect(() => {
    if (window.electronAPI?.onAIAgentLaunch) {
      window.electronAPI.onAIAgentLaunch(() => {
        setIsAgentRunning(true);
        setAgentStatus('working');
      });
    }

    if (window.electronAPI?.onAIAgentExit) {
      window.electronAPI.onAIAgentExit(() => {
        setIsAgentRunning(false);
        setAgentStatus('idle');
      });
    }

    const interval = setInterval(() => {
      setPerformanceData(prev => ({
        ...prev,
        cpu: 15 + Math.random() * 20,
        memory: 40 + Math.random() * 5
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const toggleDarkMode = useCallback(() => {
    const newDarkMode = !isDarkMode;
    dispatch(setDarkMode(newDarkMode));
    if (window.electronAPI?.setDarkMode) {
      window.electronAPI.setDarkMode(newDarkMode);
    }
  }, [isDarkMode, dispatch]);

  const startAgent = useCallback(() => {
    if (window.electronAPI?.launchAIAgent) {
      const baseURL = process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS;
      window.electronAPI.launchAIAgent(baseURL, 'system', false);
    }
  }, []);

  const stopAgent = useCallback(() => {
    window.electronAPI?.stopAIAgent?.();
  }, []);

  const navItems = useMemo(() => [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/', label: 'Quick Task', icon: Rocket },
    { path: '/threads', label: 'History', icon: MessageSquare },
    { path: '/performance', label: 'Analytics', icon: BarChart3 },
    { path: '/status', label: 'Diagnostic', icon: Search },
    { path: '/settings', label: 'System', icon: Settings }
  ], []);

  return (
    <aside className="w-72 bg-[#0d1324] border-r border-white/5 flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-white/5 bg-white/[0.02]">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
             <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center">
                <Brain className="w-6 h-6 text-slate-900" />
             </div>
             <div>
               <h2 className="text-lg font-black text-white tracking-tighter uppercase">01Agent</h2>
               <div className="flex items-center gap-1.5">
                  <div className={`w-1.5 h-1.5 rounded-full ${agentStatus === 'working' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{agentStatus}</span>
               </div>
             </div>
          </div>
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
          >
            {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-400" />}
          </button>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => (
            <NavItem
              key={item.path}
              {...item}
              active={location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path))}
              onClick={(path) => navigate(path)}
              status={agentStatus}
            />
          ))}
        </nav>
      </div>

      {/* Stats Cluster */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-thin scrollbar-thumb-white/10">
        <section>
          <div className="flex items-center gap-2 mb-4">
             <Activity className="w-3.5 h-3.5 text-emerald-400" />
             <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Real-time Vitals</h3>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-[10px] font-bold mb-1.5">
                <span className="text-slate-400 uppercase">System CPU</span>
                <span className="text-emerald-400 font-mono">{performanceData.cpu.toFixed(1)}%</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 transition-all duration-1000" style={{ width: `${performanceData.cpu}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[10px] font-bold mb-1.5">
                <span className="text-slate-400 uppercase">Memory Load</span>
                <span className="text-cyan-400 font-mono">{performanceData.memory.toFixed(1)}%</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-500 transition-all duration-1000" style={{ width: `${performanceData.memory}%` }} />
              </div>
            </div>
          </div>
        </section>

        <section>
           <div className="flex items-center gap-2 mb-4">
             <Zap className="w-3.5 h-3.5 text-amber-400" />
             <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Quick Controls</h3>
           </div>
           <div className="space-y-3">
              {!isAgentRunning ? (
                <button
                  onClick={startAgent}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-900 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all shadow-lg shadow-emerald-500/10 hover:scale-[1.02]"
                >
                  <Play className="w-3.5 h-3.5 fill-current" /> Start Engine
                </button>
              ) : (
                <button
                  onClick={stopAgent}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-rose-500/20 border border-rose-500/30 text-rose-400 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all"
                >
                  <Square className="w-3.5 h-3.5 fill-current" /> Stop Agent
                </button>
              )}
              <button className="w-full flex items-center justify-center gap-2 py-2.5 bg-white/5 border border-white/10 text-slate-400 hover:text-white rounded-xl text-[11px] font-black uppercase tracking-widest transition-all">
                <RefreshCw className="w-3.5 h-3.5" /> Purge Cache
              </button>
           </div>
        </section>
      </div>

      {/* User / Footer */}
      {user && (
        <div className="p-4 bg-white/[0.02] border-t border-white/5">
          <div className="flex items-center gap-3 p-2 rounded-xl bg-black/20 border border-white/5">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
               <UserIcon className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="min-w-0">
               <div className="text-xs font-bold text-white truncate">{user.name}</div>
               <div className="text-[10px] text-slate-500 truncate">{user.email}</div>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};

export default ModernSidebar;
