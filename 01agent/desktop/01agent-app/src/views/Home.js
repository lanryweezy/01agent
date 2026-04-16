import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import axios from '../utils/axios';
import { setLoadingDialog, setError } from '../store';
import constants from '../utils/constants';
import { useNavigate } from 'react-router-dom';
import { MdOutlineSchedule, MdSend, MdLightbulb, MdRocket } from 'react-icons/md';
import { GiBrain } from 'react-icons/gi';
import { FaRobot, FaBolt } from 'react-icons/fa';
import styled from 'styled-components';
import theme from '../theme/GlobalTheme';
import { Button, Card, TextArea, Badge } from '../components/UI/SuperiorComponents';

const HomeContainer = styled.div`
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: ${theme.spacing.xl_rem};
  position: relative;
  
  /* Animated background gradient */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.isDarkMode 
      ? 'radial-gradient(circle at 30% 70%, rgba(102, 126, 234, 0.1) 0%, transparent 50%), radial-gradient(circle at 70% 30%, rgba(0, 255, 136, 0.08) 0%, transparent 50%)'
      : 'radial-gradient(circle at 30% 70%, rgba(102, 126, 234, 0.05) 0%, transparent 50%), radial-gradient(circle at 70% 30%, rgba(0, 255, 136, 0.03) 0%, transparent 50%)'
    };
    animation: gradientShift 10s ease-in-out infinite;
    pointer-events: none;
  }
  
  @keyframes gradientShift {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }
`;

const WelcomeSection = styled.div`
  text-align: center;
  margin-bottom: ${theme.spacing.xl_rem};
  z-index: 1;
  
  h1 {
    font-size: 3rem; /* 48px / 16 = 3rem */
    font-weight: 800;
    margin-bottom: ${theme.spacing.md_rem};
    background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.accent} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeIn 0.8s ease;
  }
  
  p {
    font-size: 1.125rem; /* 18px / 16 = 1.125rem */
    color: ${props => props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary};
    margin-bottom: ${theme.spacing.lg_rem};
    animation: fadeIn 0.8s ease 0.2s both;
  }
`;

const TaskCard = styled(Card)`
  width: 100%;
  max-width: 43.75rem; /* 700px / 16 = 43.75rem */
  z-index: 1;
  animation: slideIn 0.8s ease 0.4s both;
  
  /* Enhanced glass effect */
  backdrop-filter: blur(20px);
  border: 1px solid ${props => props.isDarkMode 
    ? `${theme.colors.primary}30` 
    : `${theme.colors.primary}20`
  };
  
  &:hover {
    border-color: ${props => props.isDarkMode 
      ? `${theme.colors.primary}50` 
      : `${theme.colors.primary}40`
    };
    box-shadow: 0 20px 40px ${theme.colors.primary}20;
  }
`;

const TaskInput = styled(TextArea)`
  font-size: 1rem; /* 16px / 16 = 1rem */
  min-height: 7.5rem; /* 120px / 16 = 7.5rem */
  border: none;
  background: transparent;
  resize: none;
  
  &::placeholder {
    color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted};
    font-style: italic;
  }
  
  &:focus {
    box-shadow: none;
    border: none;
  }
`;

const ControlsRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: ${theme.spacing.lg_rem};
  gap: ${theme.spacing.md_rem};
  flex-wrap: wrap;
`;

const ModeToggles = styled.div`
  display: flex;
  gap: ${theme.spacing.sm_rem};
  flex-wrap: wrap;
`;

const ModeToggle = styled.button`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm_rem};
  padding: ${theme.spacing.sm_rem} ${theme.spacing.md_rem};
  background: ${props => props.active 
    ? `linear-gradient(135deg, ${theme.colors.primary}20 0%, ${theme.colors.accent}10 100%)`
    : 'transparent'
  };
  color: ${props => props.active 
    ? theme.colors.primary
    : (props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary)
  };
  border: 1px solid ${props => props.active 
    ? theme.colors.primary
    : (props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border)
  };
  border-radius: ${theme.radius.md};
  font-size: 0.8125rem; /* 13px / 16 = 0.8125rem */
  font-weight: 600;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${props => props.active 
      ? `linear-gradient(135deg, ${theme.colors.primary}30 0%, ${theme.colors.accent}15 100%)`
      : (props.isDarkMode ? theme.colors.dark.surfaceHover : theme.colors.light.surfaceHover)
    };
    transform: translateY(-1px);
    box-shadow: ${theme.shadows.md};
  }
  
  .icon {
    font-size: 1rem; /* 16px / 16 = 1rem */
  }
`;

const SendButton = styled(Button)`
  min-width: 7.5rem; /* 120px / 16 = 7.5rem */
  height: 3rem; /* 48px / 16 = 3rem */
  font-size: 1rem; /* 16px / 16 = 1rem */
  
  .icon {
    font-size: 1.125rem; /* 18px / 16 = 1.125rem */
  }
`;

const QuickActions = styled.div`
  display: flex;
  gap: ${theme.spacing.md_rem};
  margin-top: ${theme.spacing.xl_rem};
  flex-wrap: wrap;
  justify-content: center;
  z-index: 1;
`;

const QuickActionCard = styled.div`
  padding: ${theme.spacing.md_rem};
  background: ${props => props.isDarkMode 
    ? `linear-gradient(135deg, ${theme.colors.dark.surface} 0%, ${theme.colors.dark.background} 100%)`
    : `linear-gradient(135deg, ${theme.colors.light.surface} 0%, ${theme.colors.light.background} 100%)`
  };
  border: 1px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  border-radius: ${theme.radius.lg};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  text-align: center;
  min-width: 9.375rem; /* 150px / 16 = 9.375rem */
  
  &:hover {
    transform: translateY(-0.25rem); /* -4px / 16 = -0.25rem */
    box-shadow: ${theme.shadows.lg}, 0 0 15px ${theme.colors.primary}50; /* Added subtle glow */
    border-color: ${theme.colors.primary};
  }
  
  .icon {
    font-size: 1.5rem; /* 24px / 16 = 1.5rem */
    color: ${theme.colors.primary};
    margin-bottom: ${theme.spacing.sm_rem};
  }
  
  .title {
    font-weight: 600;
    margin-bottom: ${theme.spacing.xs_rem};
    color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
  }
  
  .description {
    font-size: 0.75rem; /* 12px / 16 = 0.75rem */
    color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted};
  }
`;

const StatsRow = styled.div`
  display: flex;
  gap: ${theme.spacing.lg_rem};
  margin-top: ${theme.spacing.xl_rem};
  justify-content: center;
  flex-wrap: wrap;
  z-index: 1;
`;

const StatItem = styled.div`
  text-align: center;
  
  .number {
    font-size: 2rem; /* 32px / 16 = 2rem */
    font-weight: 800;
    color: ${theme.colors.primary};
    line-height: 1;
  }
  
  .label {
    font-size: 0.75rem; /* 12px / 16 = 0.75rem */
    color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: ${theme.spacing.xs_rem};
  }
`;


const SuggestionsWrapper = styled.div`
  display: flex;
  gap: ${theme.spacing.sm_rem};
  margin-top: ${theme.spacing.md_rem};
  flex-wrap: wrap;
  justify-content: center;
  animation: fadeIn 0.5s ease;
`;

const SuggestionChip = styled.div`
  padding: 0.4rem 0.8rem;
  background: ${props => props.isDarkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'};
  border: 1px solid ${props => props.isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'};
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background: ${theme.colors.primary}20;
    border-color: ${theme.colors.primary};
    transform: translateY(-2px);
  }
`;

export default function Home() {
  const [messageText, setMessageText] = useState('');
  const [backgroundMode, setBackgroundMode] = useState(false);
  const [thinkingMode, setThinkingMode] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const accessToken = useSelector(state => state.accessToken);
  const isDarkMode = useSelector(state => state.isDarkMode);

  const dispatch = useDispatch();

  const navigate = useNavigate();

  const cancelRunningTask = async (tid) => {
    dispatch(setLoadingDialog(true));
    try {
      await axios.post(`/threads/${tid}/cancel_task`, {}, {
        headers: {
          'Authorization': 'Bearer ' + accessToken,
        }
      });
      dispatch(setLoadingDialog(false));
      window.electronAPI.stopAIAgent();
    } catch (error) {
      dispatch(setLoadingDialog(false));
      if (error.response.status === constants.status.BAD_REQUEST) {
        dispatch(setError(true, constants.GENERAL_ERROR));
      } else {
        dispatch(setError(true, constants.GENERAL_ERROR));
      }
      setTimeout(() => {
        dispatch(setError(false, ''));
      }, 3000);
    }
  };

  const createThread = async () => {
    if (messageText.length === 0) {
      return;
    }
    const data = {task: messageText, background_mode: backgroundMode, extended_thinking_mode: thinkingMode};
    setMessageText('');
    dispatch(setLoadingDialog(true));
    try {
      const response = await axios.post('/threads', data, {
        headers: {
          'Authorization': 'Bearer ' + accessToken,
        }
      });
      dispatch(setLoadingDialog(false));
      if (response.data.type === 'desktop_task') {
        if (!backgroundMode && response.data.is_background_mode_requested) {
          const ready = await window.electronAPI.isBackgroundModeReady();
          if (!ready) {
            // Pass the threadId to cancelRunningTask
            cancelRunningTask(response.data.thread_id);
            return;
          }
        }
        setBackgroundMode(backgroundMode || response.data.is_background_mode_requested);
        setThinkingMode(thinkingMode || response.data.is_extended_thinking_mode_requested);
        window.electronAPI.setLastThinkingModeValue((thinkingMode || response.data.is_extended_thinking_mode_requested).toString());
        window.electronAPI.launchAIAgent(
          process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS,
          response.data.thread_id,
          backgroundMode || response.data.is_background_mode_requested
        );
      }
      navigate('/threads/' + response.data.thread_id);
    } catch (error) {
      dispatch(setLoadingDialog(false));
      if (error.response.status === constants.status.BAD_REQUEST) {
        if (error.response.data?.message === 'Not_Browser_Task_BG_Mode') {
          dispatch(setError(true, 'Background Mode only supports browser tasks.'));
        } else {
          dispatch(setError(true, constants.GENERAL_ERROR));
        }
      } else {
        dispatch(setError(true, constants.GENERAL_ERROR));
      }
      setTimeout(() => {
        dispatch(setError(false, ''));
      }, 3000);
    }
  };

  const handleTextEnterKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      createThread();
    }
  };

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
    if (window.electronAPI?.onAIAgentLaunch) {
      window.electronAPI.onAIAgentLaunch((threadId) => {
        navigate('/threads/' + threadId)
      });
    }
  }, [navigate]);

  useEffect(() => {
    if (window.electronAPI?.onAIAgentExit) {
      window.electronAPI.onAIAgentExit(() => {
      });
    }
  }, []);

  useEffect(() => {
    const asyncTask = async () => {
      const lastBackgroundModeValue = await window.electronAPI.getLastBackgroundModeValue();
      setBackgroundMode(lastBackgroundModeValue === 'true');
    };
    asyncTask();
  }, [window.electronAPI]);

  useEffect(() => {
    const asyncTask = async () => {
      const lastThinkingModeValue = await window.electronAPI.getLastThinkingModeValue();
      setThinkingMode(lastThinkingModeValue === 'true');
    };
    asyncTask();
  }, [window.electronAPI]);

  useEffect(() => {
    if (window.electronAPI?.onSuggestionReceived) {
      window.electronAPI.onSuggestionReceived((data) => {
        if (data && data.suggestions) {
          setSuggestions(data.suggestions);
        }
      });
    }
  }, []);

  const quickActions = [
    {
      icon: <FaBolt />,
      title: "Quick Task",
      description: "Fast automation",
      action: () => setMessageText("Organize my desktop files")
    },
    {
      icon: <MdLightbulb />,
      title: "Smart Suggestion",
      description: "AI-powered ideas",
      action: () => setMessageText("Suggest productivity improvements for my workflow")
    },
    {
      icon: <MdRocket />,
      title: "Power User",
      description: "Advanced automation",
      action: () => setMessageText("Create a comprehensive system backup and optimization routine")
    }
  ];

  return (
    <HomeContainer isDarkMode={isDarkMode}>
      <WelcomeSection isDarkMode={isDarkMode}>
        <h1>
          <FaRobot style={{ marginRight: '16px', verticalAlign: 'middle' }} />
          01Agent
        </h1>
        <p>Lightning-fast AI desktop assistant ready to automate your world</p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Badge variant="success" isDarkMode={isDarkMode}>60-80% Faster</Badge>
          <Badge variant="info" isDarkMode={isDarkMode}>90-95% Success Rate</Badge>
          <Badge variant="primary" isDarkMode={isDarkMode}>AI-Powered</Badge>
        </div>
      </WelcomeSection>

      <TaskCard isDarkMode={isDarkMode} hover glow>
        <TaskInput
          isDarkMode={isDarkMode}
          placeholder="What would you like 01Agent to do? Be specific for best results..."
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          onKeyDown={handleTextEnterKey}
        />

        {suggestions.length > 0 && (
          <SuggestionsWrapper>
            {suggestions.map((s, i) => (
              <SuggestionChip
                key={i}
                isDarkMode={isDarkMode}
                onClick={() => setMessageText(s.ai_prompt || s.prompt)}
              >
                <MdLightbulb color={theme.colors.primary} />
                {s.title}
              </SuggestionChip>
            ))}
          </SuggestionsWrapper>
        )}
        
        <ControlsRow>
          <ModeToggles>
            <ModeToggle
              active={backgroundMode}
              isDarkMode={isDarkMode}
              onClick={() => onBGModeToggleChange(!backgroundMode)}
              aria-label="Toggle Background Mode"
            >
              <MdOutlineSchedule className="icon" />
              Background Mode
            </ModeToggle>
            
            <ModeToggle
              active={thinkingMode}
              isDarkMode={isDarkMode}
              onClick={() => setThinkingMode(!thinkingMode)}
              aria-label="Toggle Deep Thinking Mode"
            >
              <GiBrain className="icon" />
              Deep Thinking
            </ModeToggle>
          </ModeToggles>
          
          <SendButton
            variant="primary"
            size="lg"
            disabled={messageText.length === 0}
            onClick={createThread}
            isDarkMode={isDarkMode}
            aria-label="Execute Task"
          >
            <MdSend className="icon" />
            Execute Task
          </SendButton>
        </ControlsRow>
      </TaskCard>

      <QuickActions>
        {quickActions.map((action, index) => (
          <QuickActionCard
            key={index}
            isDarkMode={isDarkMode}
            onClick={action.action}
          >
            <div className="icon">{action.icon}</div>
            <div className="title">{action.title}</div>
            <div className="description">{action.description}</div>
          </QuickActionCard>
        ))}
      </QuickActions>

      <StatsRow>
        <StatItem isDarkMode={isDarkMode}>
          <div className="number">60-80%</div>
          <div className="label">Faster Execution</div>
        </StatItem>
        <StatItem isDarkMode={isDarkMode}>
          <div className="number">90-95%</div>
          <div className="label">Success Rate</div>
        </StatItem>
        <StatItem isDarkMode={isDarkMode}>
          <div className="number">50%</div>
          <div className="label">Less CPU Usage</div>
        </StatItem>
      </StatsRow>
    </HomeContainer>
  );
}
