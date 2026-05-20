import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import axios from '../utils/axios';
import constants from '../utils/constants';
import { setLoadingDialog, setError } from '../store';
import ChatMessage from '../components/ChatMessage';
import ThreadDialog from '../components/DataDialogs/ThreadDialog';
import YesNoDialog from '../components/Elements/YesNoDialog';
import {
  Edit2,
  Trash2,
  Send,
  Square,
  Mic,
  MicOff,
  Clock,
  Brain,
  Terminal,
  Activity,
  Cpu,
  Layers,
  ChevronRight
} from 'lucide-react';
import { ClipLoader } from 'react-spinners';

export default function Thread() {
  const [thread, setThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [isSendingMessage, setSendingMessage] = useState(false);
  const [backgroundMode, setBackgroundMode] = useState(false);
  const [thinkingMode, setThinkingMode] = useState(false);

  const [isThreadDialogOpen, setThreadDialogOpen] = useState(false);
  const [isDeleteThreadDialogOpen, setDeleteThreadDialogOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [agentStatus, setAgentStatus] = useState(null);

  const accessToken = useSelector(state => state.accessToken);
  const isDarkMode = useSelector(state => state.isDarkMode);
  const { tid } = useParams();
  const bottomRef = useRef(null);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const getThread = useCallback(() => {
    dispatch(setLoadingDialog(true));
    axios.get(`/threads/${tid}`, {
      headers: { 'Authorization': 'Bearer ' + accessToken }
    }).then(response => {
      setThread(response.data);
      dispatch(setLoadingDialog(false));
    }).catch(error => {
      dispatch(setLoadingDialog(false));
      if (error.response?.status === constants.status.UNAUTHORIZED) {
        window.location.reload();
      }
    });
  }, [tid, accessToken, dispatch]);

  const getThreadMessages = useCallback(() => {
    dispatch(setLoadingDialog(true));
    axios.get(`/threads/${tid}/thread_messages`, {
      headers: { 'Authorization': 'Bearer ' + accessToken }
    }).then(response => {
      setMessages(response.data);
      dispatch(setLoadingDialog(false));
    }).catch(error => {
      dispatch(setLoadingDialog(false));
      if (error.response?.status === constants.status.UNAUTHORIZED) {
        window.location.reload();
      }
    });
  }, [tid, accessToken, dispatch]);

  const sendMessage = () => {
    if (messageText.length === 0 || isSendingMessage || thread.status === 'working') {
      return;
    }
    
    const data = {
      text: messageText.trim(),
      background_mode: backgroundMode,
      extended_thinking_mode: thinkingMode
    };
    setMessageText('');
    setSendingMessage(true);
    dispatch(setLoadingDialog(true));
    axios.post(`/threads/${tid}/send_message`, data, {
      headers: { 'Authorization': 'Bearer ' + accessToken }
    }).then(async (response) => {
      dispatch(setLoadingDialog(false));
      setSendingMessage(false);
      if (response.data.type === 'desktop_task') {
        if (!backgroundMode && response.data.is_background_mode_requested) {
          const ready = await window.electronAPI.isBackgroundModeReady();
          if (!ready) {
            cancelRunningTask();
            return;
          }
        }
        const newBG = backgroundMode || response.data.is_background_mode_requested;
        const newThinking = thinkingMode || response.data.is_extended_thinking_mode_requested;
        setBackgroundMode(newBG);
        setThinkingMode(newThinking);
        window.electronAPI.setLastThinkingModeValue(newThinking.toString());
        window.electronAPI.launchAIAgent(
          process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS,
          tid,
          newBG
        );
      }
      getThread();
      getThreadMessages();
    }).catch((error) => {
      dispatch(setLoadingDialog(false));
      setSendingMessage(false);
      const msg = error.response?.data?.message === 'Not_Browser_Task_BG_Mode'
        ? 'Background Mode only supports browser tasks.'
        : 'Something Wrong Happened, Please try again.';
      dispatch(setError(true, msg));
      setTimeout(() => dispatch(setError(false, '')), 3000);
    });
  };

  const deleteThread = useCallback(() => {
    dispatch(setLoadingDialog(true));
    axios.delete('/threads/' + tid, {
      headers: { 'Authorization': 'Bearer ' + accessToken }
    }).then(() => {
      dispatch(setLoadingDialog(false));
      navigate('/');
      window.location.reload();
    }).catch((error) => {
      dispatch(setLoadingDialog(false));
      if (error.response?.status === constants.status.UNAUTHORIZED) {
        window.location.reload();
      } else {
        dispatch(setError(true, constants.GENERAL_ERROR));
        setTimeout(() => dispatch(setError(false, '')), 3000);
      }
    });
  }, [dispatch, tid, accessToken, navigate]);

  const cancelRunningTask = () => {
    if (thread.status !== 'working') return;
    dispatch(setLoadingDialog(true));
    axios.post(`/threads/${tid}/cancel_task`, {}, {
      headers: { 'Authorization': 'Bearer ' + accessToken }
    }).then(() => {
      dispatch(setLoadingDialog(false));
      window.electronAPI.stopAIAgent();
      getThreadMessages();
      getThread();
    }).catch(() => {
      dispatch(setLoadingDialog(false));
      dispatch(setError(true, constants.GENERAL_ERROR));
      setTimeout(() => dispatch(setError(false, '')), 3000);
    });
  };

  const handleTextEnterKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleVoice = () => {
    if (isListening) stopListening();
    else startListening();
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      dispatch(setError(true, 'Speech recognition not supported in this browser.'));
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);
    recognition.onresult = (e) => setMessageText(e.results[0][0].transcript);
    recognition.start();
  };

  const stopListening = () => setIsListening(false);

  const onBGModeToggleChange = async (value) => {
    if (value) {
      const ready = await window.electronAPI.isBackgroundModeReady();
      if (!ready) {
        window.electronAPI.startBackgroundSetup();
        return;
      }
    }
    setBackgroundMode(value);
  };

  useEffect(() => {
    getThread();
    getThreadMessages();
  }, [tid, getThread, getThreadMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (window.electronAPI?.onAIAgentLaunch) {
      window.electronAPI.onAIAgentLaunch(() => window.location.reload());
    }
  }, []);

  useEffect(() => {
    if (window.electronAPI?.onAIAgentExit) {
      window.electronAPI.onAIAgentExit(() => {
        getThread();
        getThreadMessages();
      });
    }
  }, [getThread, getThreadMessages]);

  useEffect(() => {
    const fetchSettings = async () => {
      const lastBG = await window.electronAPI.getLastBackgroundModeValue();
      const lastThinking = await window.electronAPI.getLastThinkingModeValue();
      setBackgroundMode(lastBG === 'true');
      setThinkingMode(lastThinking === 'true');
    };
    fetchSettings();
  }, []);

  useEffect(() => {
    if (window.electronAPI?.onAgentStatus) {
      window.electronAPI.onAgentStatus((data) => setAgentStatus(data));
    }
  }, []);

  const memoizedThreadObj = useMemo(() => thread !== null ? { ...thread } : null, [thread]);
  const handleDialogSuccess = useCallback(() => window.location.reload(), []);

  const memoizedMessageList = useMemo(() => (
    messages.map((msg) => (
      <ChatMessage key={'thread_message__' + msg.id} message={msg} />
    ))
  ), [messages]);

  if (!thread) return <div className="flex-1 flex items-center justify-center"><ClipLoader color="#00ff88" /></div>;

  return (
    <div className="flex flex-row h-full overflow-hidden bg-[#0a0f1d] text-slate-200">
      <ThreadDialog
        isOpen={isThreadDialogOpen}
        setOpen={setThreadDialogOpen}
        threadObj={memoizedThreadObj}
        onSuccess={handleDialogSuccess}
      />
      <YesNoDialog
        isOpen={isDeleteThreadDialogOpen}
        setOpen={setDeleteThreadDialogOpen}
        title='Delete Thread'
        text='Are you sure that you want to delete this thread?'
        onYesClicked={deleteThread}
        isDarkMode={true}
      />

      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/[0.02] backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 flex items-center justify-center border border-emerald-500/30">
              <Terminal className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white truncate max-w-md">{thread.title}</h2>
              <div className="flex items-center gap-2 mt-0.5">
                <div className={`w-2 h-2 rounded-full ${thread.status === 'working' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`}></div>
                <span className="text-xs text-slate-400 uppercase tracking-wider">{thread.status}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setThreadDialogOpen(true)}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors text-slate-400 hover:text-emerald-400"
            >
              <Edit2 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setDeleteThreadDialogOpen(true)}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors text-slate-400 hover:text-rose-400"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
          {memoizedMessageList}
          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gradient-to-t from-[#0a0f1d] to-transparent">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-3 backdrop-blur-xl focus-within:border-emerald-500/50 transition-all shadow-2xl">
              <textarea
                className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-slate-500 resize-none px-2 py-1"
                placeholder="What do you want 01Agent to do?"
                rows="2"
                value={messageText}
                onKeyDown={handleTextEnterKey}
                onChange={(e) => setMessageText(e.target.value)}
              />

              <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onBGModeToggleChange(!backgroundMode)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      backgroundMode
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-white/5 text-slate-400 border border-white/5 hover:bg-white/10'
                    }`}
                  >
                    <Clock className="w-3.5 h-3.5" />
                    Background
                  </button>
                  <button
                    onClick={() => setThinkingMode(!thinkingMode)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      thinkingMode
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'bg-white/5 text-slate-400 border border-white/5 hover:bg-white/10'
                    }`}
                  >
                    <Brain className="w-3.5 h-3.5" />
                    Thinking
                  </button>
                  <button
                    onClick={toggleVoice}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      isListening
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-white/5 text-slate-400 border border-white/5 hover:bg-white/10'
                    }`}
                  >
                    {isListening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
                    Voice
                  </button>
                </div>

                <div className="flex items-center gap-3">
                  {isSendingMessage ? (
                    <ClipLoader color="#10b981" size={24} />
                  ) : thread.status === 'working' ? (
                    <button
                      onClick={cancelRunningTask}
                      className="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center border border-rose-500/30 hover:bg-rose-500/30 transition-all"
                    >
                      <Square className="w-5 h-5 fill-current" />
                    </button>
                  ) : (
                    <button
                      disabled={messageText.trim().length === 0}
                      onClick={sendMessage}
                      className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
                        messageText.trim().length > 0
                          ? 'bg-emerald-500 text-slate-900 shadow-lg shadow-emerald-500/20 hover:scale-105 active:scale-95'
                          : 'bg-white/5 text-slate-600 cursor-not-allowed'
                      }`}
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Sidebar */}
      <aside className="w-72 border-l border-white/5 bg-black/20 backdrop-blur-md hidden xl:flex flex-col p-6 overflow-y-auto">
        <div className="flex items-center gap-2 mb-8">
          <Activity className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-bold uppercase tracking-widest text-emerald-400">System Insight</h3>
        </div>

        <div className="space-y-6">
          <section>
            <h4 className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-4">Resource Usage</h4>
            <div className="space-y-4">
              <div className="bg-white/[0.03] rounded-xl p-4 border border-white/5">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Cpu className="w-3.5 h-3.5" />
                    CPU Load
                  </div>
                  <span className="text-xs font-mono text-emerald-400">{agentStatus?.cpu.toFixed(1) || '0.0'}%</span>
                </div>
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 transition-all duration-500"
                    style={{ width: `${agentStatus?.cpu || 0}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white/[0.03] rounded-xl p-4 border border-white/5">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Layers className="w-3.5 h-3.5" />
                    Memory
                  </div>
                  <span className="text-xs font-mono text-emerald-400">{agentStatus?.memory.toFixed(1) || '0.0'}%</span>
                </div>
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 transition-all duration-500"
                    style={{ width: `${agentStatus?.memory || 0}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h4 className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-4">Active Context</h4>
            <div className="bg-white/[0.03] rounded-xl p-4 border border-white/5">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <ChevronRight className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="min-w-0">
                  <div className="text-[10px] text-slate-500 uppercase">Current Window</div>
                  <div className="text-xs text-white truncate font-medium">{agentStatus?.active_window || 'Idle'}</div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <div className="mt-auto pt-8 border-t border-white/5">
          <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
            <span>AGENT_CORE</span>
            <span className="text-emerald-500/50">v2.2.0-STABLE</span>
          </div>
        </div>
      </aside>
    </div>
  );
}
