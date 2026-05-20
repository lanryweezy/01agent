import React, { useState, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import axios from '../utils/axios';
import { setLoadingDialog, setError } from '../store';
import constants from '../utils/constants';
import { useNavigate } from 'react-router-dom';
import {
  Send,
  Brain,
  Rocket,
  Clock,
  Zap,
  Activity,
  Monitor,
  Lightbulb,
  Cpu,
  ShieldCheck,
  ChevronRight,
  Terminal
} from 'lucide-react';
import { ClipLoader } from 'react-spinners';

const SuggestionChip = ({ children, onClick }) => (
  <button
    onClick={onClick}
    className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-xs text-slate-400 hover:bg-emerald-500/10 hover:border-emerald-500/30 hover:text-emerald-400 transition-all active:scale-95"
  >
    <Lightbulb className="w-3.5 h-3.5" />
    {children}
  </button>
);

const QuickActionCard = ({ icon: Icon, title, description, onClick }) => (
  <button
    onClick={onClick}
    className="group flex flex-col items-center text-center p-6 bg-white/[0.03] border border-white/10 rounded-3xl hover:bg-white/[0.06] hover:border-emerald-500/30 hover:shadow-2xl hover:shadow-emerald-500/10 transition-all hover:-translate-y-1"
  >
    <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <Icon className="w-6 h-6 text-emerald-400" />
    </div>
    <h3 className="text-sm font-bold text-white mb-1 uppercase tracking-wider">{title}</h3>
    <p className="text-[10px] text-slate-500 font-medium">{description}</p>
  </button>
);

export default function Home() {
  const [messageText, setMessageText] = useState('');
  const [backgroundMode, setBackgroundMode] = useState(false);
  const [thinkingMode, setThinkingMode] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const accessToken = useSelector(state => state.accessToken);
  const isDarkMode = useSelector(state => state.isDarkMode);

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const createThread = async () => {
    if (messageText.trim().length === 0) return;

    const data = {
      task: messageText.trim(),
      background_mode: backgroundMode,
      extended_thinking_mode: thinkingMode
    };

    setMessageText('');
    dispatch(setLoadingDialog(true));

    try {
      const response = await axios.post('/threads', data, {
        headers: { 'Authorization': 'Bearer ' + accessToken }
      });

      dispatch(setLoadingDialog(false));

      if (response.data.type === 'desktop_task') {
        const needsBG = !backgroundMode && response.data.is_background_mode_requested;
        if (needsBG) {
          const ready = await window.electronAPI.isBackgroundModeReady();
          if (!ready) {
             window.electronAPI.startBackgroundSetup();
             return;
          }
        }

        const finalBG = backgroundMode || response.data.is_background_mode_requested;
        const finalThinking = thinkingMode || response.data.is_extended_thinking_mode_requested;

        window.electronAPI.setLastThinkingModeValue(finalThinking.toString());
        window.electronAPI.launchAIAgent(
          process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS,
          response.data.thread_id,
          finalBG
        );
      }
      navigate('/threads/' + response.data.thread_id);
    } catch (error) {
      dispatch(setLoadingDialog(false));
      const msg = error.response?.data?.message === 'Not_Browser_Task_BG_Mode'
        ? 'Background Mode only supports browser tasks.'
        : constants.GENERAL_ERROR;
      dispatch(setError(true, msg));
      setTimeout(() => dispatch(setError(false, '')), 3000);
    }
  };

  const handleTextEnterKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      createThread();
    }
  };

  useEffect(() => {
    const fetchModes = async () => {
      const lastBG = await window.electronAPI.getLastBackgroundModeValue();
      const lastThinking = await window.electronAPI.getLastThinkingModeValue();
      setBackgroundMode(lastBG === 'true');
      setThinkingMode(lastThinking === 'true');
    };
    fetchModes();
  }, []);

  useEffect(() => {
    if (window.electronAPI?.onSuggestionReceived) {
      window.electronAPI.onSuggestionReceived((data) => {
        if (data?.suggestions) setSuggestions(data.suggestions);
      });
    }
  }, []);

  const memoizedSuggestions = useMemo(() => (
    suggestions.map((s, i) => (
      <SuggestionChip key={i} onClick={() => setMessageText(s.ai_prompt || s.prompt)}>
        {s.title}
      </SuggestionChip>
    ))
  ), [suggestions]);

  return (
    <div className="flex-1 h-full bg-[#0a0f1d] overflow-hidden flex flex-col relative">
      {/* Animated Background Highlights */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-500/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="flex-1 flex flex-col items-center justify-center p-8 z-10 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">

        {/* Brand / Welcome */}
        <div className="text-center mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
           <div className="inline-flex items-center gap-4 mb-4">
             <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-2xl shadow-emerald-500/20">
               <Rocket className="w-10 h-10 text-slate-900" />
             </div>
             <h1 className="text-5xl font-black text-white tracking-tighter">01Agent</h1>
           </div>
           <p className="text-slate-400 text-lg font-medium max-w-lg mx-auto leading-relaxed">
             Hyper-automated AI desktop companion. <span className="text-emerald-500">60-80% faster</span> execution than legacy agents.
           </p>

           <div className="flex justify-center gap-3 mt-6">
              <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <ShieldCheck className="w-3 h-3 text-emerald-400" /> Precision Grade
              </div>
              <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Zap className="w-3 h-3 text-cyan-400" /> Low Latency
              </div>
           </div>
        </div>

        {/* Input Terminal */}
        <div className="w-full max-w-3xl animate-in fade-in slide-in-from-bottom-6 duration-1000 delay-200">
          <div className="bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-4 backdrop-blur-3xl shadow-2xl focus-within:border-emerald-500/40 transition-all">
            <div className="px-4 pt-4 pb-2">
              <textarea
                className="w-full bg-transparent border-none focus:ring-0 text-xl text-white placeholder-slate-600 resize-none min-h-[120px]"
                placeholder="What task should 01Agent perform today?"
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                onKeyDown={handleTextEnterKey}
              />
            </div>

            {suggestions.length > 0 && (
              <div className="flex flex-wrap gap-2 px-4 pb-4">
                {memoizedSuggestions}
              </div>
            )}

            <div className="flex items-center justify-between p-2 border-t border-white/5 mt-2">
              <div className="flex gap-2">
                <button
                  onClick={() => setBackgroundMode(!backgroundMode)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-2xl text-[11px] font-bold transition-all border ${
                    backgroundMode
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-lg shadow-emerald-500/5'
                      : 'bg-white/5 border-white/5 text-slate-500 hover:text-slate-300'
                  }`}
                >
                  <Clock className="w-3.5 h-3.5" /> BACKGROUND
                </button>
                <button
                  onClick={() => setThinkingMode(!thinkingMode)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-2xl text-[11px] font-bold transition-all border ${
                    thinkingMode
                      ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 shadow-lg shadow-cyan-500/5'
                      : 'bg-white/5 border-white/5 text-slate-500 hover:text-slate-300'
                  }`}
                >
                  <Brain className="w-3.5 h-3.5" /> THINKING
                </button>
              </div>

              <button
                disabled={messageText.trim().length === 0}
                onClick={createThread}
                className={`flex items-center gap-2 px-8 py-3 rounded-2xl font-black uppercase tracking-widest text-xs transition-all ${
                  messageText.trim().length > 0
                    ? 'bg-emerald-500 text-slate-900 hover:bg-emerald-400 hover:scale-[1.02] shadow-xl shadow-emerald-500/20 active:scale-95'
                    : 'bg-white/5 text-slate-700 cursor-not-allowed grayscale'
                }`}
              >
                <Send className="w-4 h-4" /> EXECUTE TASK
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="w-full max-w-4xl grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-500">
          <QuickActionCard
            icon={Monitor}
            title="UI Flow"
            description="Native automation"
            onClick={() => setMessageText("Organize my downloads folder by file type")}
          />
          <QuickActionCard
            icon={Terminal}
            title="Dev Ops"
            description="Terminal logic"
            onClick={() => setMessageText("Check my local docker containers and status")}
          />
          <QuickActionCard
            icon={Activity}
            title="Monitor"
            description="System vitals"
            onClick={() => setMessageText("Analyze my CPU usage over the last 5 minutes")}
          />
          <QuickActionCard
            icon={Cpu}
            title="Reasoning"
            description="Deep analysis"
            onClick={() => setMessageText("Summarize the current state of my open browser tabs")}
          />
        </div>

        {/* Status Metrics Footer */}
        <div className="mt-20 pt-8 border-t border-white/5 w-full max-w-2xl flex justify-around animate-in fade-in duration-1000 delay-700">
           <div className="text-center">
             <div className="text-2xl font-black text-white">94%</div>
             <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">Efficiency Rate</div>
           </div>
           <div className="text-center">
             <div className="text-2xl font-black text-white">0.02s</div>
             <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">Input Latency</div>
           </div>
           <div className="text-center">
             <div className="text-2xl font-black text-white">100%</div>
             <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">Native Control</div>
           </div>
        </div>

      </div>
    </div>
  );
}
