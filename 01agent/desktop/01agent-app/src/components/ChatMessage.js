import React, { useMemo } from 'react';
import { useSelector } from 'react-redux';
import {
  MousePointer2,
  Keyboard,
  CheckCircle2,
  Scroll,
  Pause,
  ExternalLink,
  Move,
  AlertCircle,
  LayoutGrid,
  Monitor,
  CornerDownRight,
  Brain,
  Code,
  Box,
  Terminal,
  Activity
} from 'lucide-react';

const iconClass = "w-4 h-4 text-emerald-400";

const actionMap = {
  mouse_move: { label: 'Move Cursor', color: 'emerald', icon: <MousePointer2 className={iconClass} /> },
  left_click: { label: 'Click', color: 'emerald', icon: <MousePointer2 className={iconClass} /> },
  right_click: { label: 'Right Click', color: 'emerald', icon: <MousePointer2 className={iconClass} /> },
  double_click: { label: 'Double Click', color: 'emerald', icon: <MousePointer2 className={iconClass} /> },
  triple_click: { label: 'Triple Click', color: 'emerald', icon: <MousePointer2 className={iconClass} /> },
  left_click_drag: { label: 'Click & Drag', color: 'emerald', icon: <Move className={iconClass} /> },
  left_mouse_down: { label: 'Mouse Down', color: 'emerald', icon: <Move className={iconClass} /> },
  left_mouse_up: { label: 'Mouse Up', color: 'emerald', icon: <Move className={iconClass} /> },
  scroll: { label: 'Scroll', color: 'emerald', icon: <Scroll className={iconClass} /> },
  type: { label: 'Type Text', color: 'emerald', icon: <Keyboard className={iconClass} /> },
  key: { label: 'Press Key', color: 'emerald', icon: <Keyboard className={iconClass} /> },
  hold_key: { label: 'Hold Key', color: 'emerald', icon: <Keyboard className={iconClass} /> },
  key_combo: { label: 'Key Combo', color: 'emerald', icon: <Keyboard className={iconClass} /> },
  wait: { label: 'Wait', color: 'slate', icon: <Pause className="w-4 h-4 text-slate-400" /> },
  launch_browser: { label: 'Launch Browser', color: 'cyan', icon: <ExternalLink className="w-4 h-4 text-cyan-400" /> },
  launch_app: { label: 'Launch App', color: 'emerald', icon: <LayoutGrid className={iconClass} /> },
  focus_app: { label: 'Switch To App', color: 'emerald', icon: <LayoutGrid className={iconClass} /> },
  request_screenshot: { label: 'Capture Screen', color: 'emerald', icon: <Monitor className={iconClass} /> },
  tool_use: { label: 'Tool Exec', color: 'emerald', icon: <Terminal className={iconClass} /> },
  subtask_completed: { label: 'Step Success', color: 'emerald', icon: <CheckCircle2 className={iconClass} /> },
  subtask_failed: { label: 'Step Error', color: 'rose', icon: <AlertCircle className="w-4 h-4 text-rose-400" /> }
};

const Tag = ({ children, color = "emerald" }) => {
  const colors = {
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    cyan: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    rose: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    slate: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider border ${colors[color] || colors.emerald}`}>
      {children}
    </span>
  );
};

const ThoughtBox = ({ children, title = "REASONING" }) => (
  <div className="mt-3 bg-black/30 border border-white/5 rounded-lg overflow-hidden">
    <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border-b border-white/5">
      <Brain className="w-3.5 h-3.5 text-cyan-400" />
      <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">{title}</span>
    </div>
    <div className="p-3 text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap italic opacity-80">
      {children}
    </div>
  </div>
);

const Label = ({ children }) => (
  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter mr-2">{children}</span>
);

const ChatMessage = React.memo(({ message }) => {
  const isUser = message.thread_chat_from !== 'from_ai';

  const parsedMessage = useMemo(() => {
    if (message.thread_chat_type === 'normal_message') return null;
    try {
      return JSON.parse(message.text);
    } catch {
      return null;
    }
  }, [message.text, message.thread_chat_type]);

  const memoizedContent = useMemo(() => {
    const type = message.thread_chat_type;
    const raw = message.text;

    if (type === 'normal_message') return <div className="text-[14.5px] text-slate-200 leading-relaxed">{raw}</div>;

    let parsed = parsedMessage;
    if (!parsed) return <div className="text-rose-400 text-xs italic">[Unparsable System Event]</div>;

    if (type === 'classification') {
      const isDesktop = parsed.type === 'desktop_task';
      return (
        <div className="space-y-3">
          <Tag color={isDesktop ? 'emerald' : 'cyan'}>
            {isDesktop ? <Monitor className="w-3 h-3" /> : <CornerDownRight className="w-3 h-3" />}
            {isDesktop ? 'Desktop Automation' : 'User Inquiry'}
          </Tag>
          <div className="text-[14.5px] text-slate-300">{parsed.response}</div>
        </div>
      );
    }

    if (type === 'action') {
      const actionMeta = actionMap[parsed.action] || { label: parsed.action, icon: <Activity className={iconClass} /> };
      return (
        <div className="space-y-2">
          <Tag color={actionMeta.color}>{actionMeta.icon}{actionMeta.label}</Tag>
          <div className="text-sm text-slate-300 grid gap-1 ml-1">
            {parsed.action === 'tool_use' && (
              <>
                <div><Label>EXECUTING:</Label><span className="font-mono text-emerald-400">{parsed.tool}</span></div>
                {parsed.args && <div className="bg-black/20 p-2 rounded mt-1 font-mono text-[11px] border border-white/5"><Label>PARAMS:</Label>{JSON.stringify(parsed.args)}</div>}
              </>
            )}
            {parsed.text && <div><Label>INPUT:</Label>{parsed.text}</div>}
            {parsed.url && <div><Label>TARGET:</Label><span className="text-cyan-400 underline">{parsed.url}</span></div>}
            {parsed.app_name && <div><Label>APP:</Label>{parsed.app_name}</div>}
            {parsed.coordinate && <div><Label>POS:</Label><span className="font-mono text-xs">({parsed.coordinate.x}, {parsed.coordinate.y})</span></div>}
          </div>
          {parsed.reasoning && <ThoughtBox>{parsed.reasoning}</ThoughtBox>}
        </div>
      );
    }

    if (type === 'browser_use' || type === 'bg_mode_browser' || type === 'bg_mode_browser_v2') {
      return (
        <div className="space-y-3">
          <Tag color="cyan"><ExternalLink className="w-3 h-3" />Web Browser Protocol</Tag>
          {parsed.current_state && (
            <div className="text-xs space-y-2 text-slate-400 bg-white/5 p-3 rounded-lg border border-white/5">
              <div><Label>EVAL:</Label>{parsed.current_state.evaluation_previous_goal || parsed.current_state.current_evaluation}</div>
              <div><Label>MEM:</Label>{parsed.current_state.memory}</div>
              <div className="text-cyan-400"><Label>NEXT:</Label>{parsed.current_state.next_goal || parsed.current_state.next_steps}</div>
            </div>
          )}
          {parsed.actions && (
             <div className="space-y-2">
                {parsed.actions.map((act, i) => (
                  <div key={i} className="flex items-center gap-2 text-[11px] font-mono text-emerald-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/50" />
                    {act.action} ({JSON.stringify(act.params)})
                  </div>
                ))}
             </div>
          )}
        </div>
      );
    }

    if (type === 'desktop_use' || type === 'desktop_use_v2') {
      return (
        <div className="space-y-3">
          <Tag><Monitor className="w-3 h-3" />Native OS Execution</Tag>
          {parsed.current_state && (
            <div className="text-xs space-y-2 text-slate-400 bg-white/5 p-3 rounded-lg border border-white/5">
              <div><Label>EVAL:</Label>{parsed.current_state.current_evaluation || parsed.current_state.evaluation_previous_goal}</div>
              <div className="text-emerald-400"><Label>PLAN:</Label>{parsed.current_state.next_steps || parsed.current_state.next_goal}</div>
            </div>
          )}
          {parsed.action && (
            <div className="flex items-center gap-3 bg-emerald-500/5 p-2 rounded border border-emerald-500/10">
               {actionMap[parsed.action]?.icon || <Activity className={iconClass} />}
               <span className="text-xs font-bold text-emerald-400 uppercase">{parsed.action}</span>
            </div>
          )}
        </div>
      );
    }

    if (type === 'plan') {
      return (
        <div className="space-y-4">
          <Tag color="cyan"><Code className="w-3 h-3" />Strategic Plan</Tag>
          <div className="space-y-2 ml-1">
            {parsed.subtasks?.map((step, idx) => (
              <div key={idx} className="flex items-start gap-3 group">
                <div className="mt-1 w-5 h-5 rounded bg-white/5 flex items-center justify-center text-[10px] font-bold text-slate-500 border border-white/5 group-hover:border-cyan-500/30 transition-colors">
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <div className="text-xs text-slate-200">{step.subtask}</div>
                  <div className="text-[9px] uppercase tracking-tighter text-slate-500">Layer: {step.type}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (type === 'thinking' && message.chain_of_thought) {
      return <ThoughtBox title="EXTENDED THINKING">{message.chain_of_thought}</ThoughtBox>;
    }

    return <div className="text-xs text-slate-500">[System Interaction Layer: {type}]</div>;
  }, [message.thread_chat_type, message.text, parsedMessage, message.chain_of_thought]);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} group animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      <div className={`
        relative max-w-[85%] xl:max-w-[70%] p-4 rounded-2xl border transition-all
        ${isUser
          ? 'bg-emerald-600/10 border-emerald-500/20 rounded-tr-none'
          : 'bg-white/[0.03] border-white/10 rounded-tl-none backdrop-blur-sm'
        }
      `}>
        {memoizedContent}

        {/* Timestamp/Role hint */}
        <div className={`absolute -bottom-5 text-[9px] font-bold tracking-widest uppercase opacity-0 group-hover:opacity-40 transition-opacity whitespace-nowrap ${isUser ? 'right-0 text-emerald-500' : 'left-0 text-slate-400'}`}>
           {isUser ? 'Primary User' : 'Core AI Proxy'}
        </div>
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  return prevProps.message.id === nextProps.message.id &&
         prevProps.message.text === nextProps.message.text &&
         prevProps.message.thread_chat_type === nextProps.message.thread_chat_type &&
         prevProps.message.chain_of_thought === nextProps.message.chain_of_thought;
});

export default ChatMessage;
ChatMessage.displayName = 'ChatMessage';
