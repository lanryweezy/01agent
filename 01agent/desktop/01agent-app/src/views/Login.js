import React from 'react';
import {
  Rocket,
  ShieldCheck,
  Zap,
  ChevronRight,
  Brain,
  Monitor,
  Terminal,
  Activity
} from 'lucide-react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { setAccessToken, setUser } from '../store';

const Login = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleEnterDemo = () => {
    // Mock login for demo purposes
    dispatch(setAccessToken('demo-token'));
    dispatch(setUser({ name: 'Alpha Tester', email: 'alpha@01agent.ai' }));
    navigate('/');
  };

  return (
    <div className="min-h-screen w-full bg-[#0a0f1d] flex items-center justify-center relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-emerald-500/10 blur-[150px] rounded-full animate-pulse" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-cyan-500/10 blur-[150px] rounded-full animate-pulse" />

      <div className="w-full max-w-md p-8 relative z-10 animate-in fade-in zoom-in duration-700">
        <div className="bg-white/[0.03] border border-white/10 rounded-[3rem] p-10 backdrop-blur-3xl shadow-2xl">
          {/* Logo Section */}
          <div className="flex flex-col items-center text-center mb-10">
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center mb-6 shadow-2xl shadow-emerald-500/20 ring-4 ring-white/5">
              <Brain className="w-12 h-12 text-slate-900" />
            </div>
            <h1 className="text-4xl font-black text-white tracking-tighter mb-2">01Agent</h1>
            <p className="text-slate-400 font-medium">AI Native Desktop Orchestrator</p>
          </div>

          {/* Action Area */}
          <div className="space-y-6">
            <button
              onClick={handleEnterDemo}
              className="group w-full py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-900 rounded-2xl font-black uppercase tracking-widest text-sm transition-all shadow-xl shadow-emerald-500/20 hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-3"
            >
              <Rocket className="w-5 h-5 group-hover:animate-bounce" />
              Enter Control Center
            </button>

            <div className="pt-8 border-t border-white/5">
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-4 text-center">Core Capabilities</h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-xl border border-white/5">
                  <Monitor className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-[10px] font-bold text-slate-300 uppercase">Native OS</span>
                </div>
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-xl border border-white/5">
                  <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="text-[10px] font-bold text-slate-300 uppercase">Command</span>
                </div>
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-xl border border-white/5">
                  <Activity className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-[10px] font-bold text-slate-300 uppercase">Realtime</span>
                </div>
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-xl border border-white/5">
                  <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="text-[10px] font-bold text-slate-300 uppercase">Trusted</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase opacity-40 hover:opacity-100 transition-opacity">
            Autonomous Proxy Instance • Ready for Connection
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
