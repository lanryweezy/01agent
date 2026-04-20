import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import axios from '../utils/axios';
import { setLoadingDialog, setError } from '../store';
import constants from '../utils/constants';
import { useNavigate } from 'react-router-dom';
import { MdSend, MdLightbulb, MdRocket } from 'react-icons/md';
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
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: ${theme.spacing.md_rem};
    background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.accent} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeIn 0.8s ease;
  }
  
  p {
    font-size: 1.125rem;
    color: ${props => props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary};
    margin-bottom: ${theme.spacing.lg_rem};
    animation: fadeIn 0.8s ease 0.2s both;
  }

  .engine-badge {
    display: inline-block;
    padding: 2px 8px;
    background: ${theme.colors.accent}20;
    border: 1px solid ${theme.colors.accent};
    border-radius: 4px;
    color: ${theme.colors.accent};
    font-size: 0.75rem;
    font-weight: bold;
    margin-bottom: 1rem;
    letter-spacing: 1px;
    text-transform: uppercase;
  }
`;

const TaskCard = styled(Card)`
  width: 100%;
  max-width: 43.75rem;
  z-index: 1;
  animation: slideIn 0.8s ease 0.4s both;
  backdrop-filter: blur(20px);
  border: 1px solid ${props => props.isDarkMode ? `${theme.colors.primary}30` : `${theme.colors.primary}20`};
  
  &:hover {
    border-color: ${props => props.isDarkMode ? `${theme.colors.primary}50` : `${theme.colors.primary}40`};
    box-shadow: 0 20px 40px ${theme.colors.primary}20;
  }
`;

const TaskInput = styled(TextArea)`
  font-size: 1rem;
  min-height: 7.5rem;
  border: none;
  background: transparent;
  resize: none;
  
  &::placeholder {
    color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted};
    font-style: italic;
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
  background: ${props => props.active ? `linear-gradient(135deg, ${theme.colors.primary}20 0%, ${theme.colors.accent}10 100%)` : 'transparent'};
  color: ${props => props.active ? theme.colors.primary : (props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary)};
  border: 1px solid ${props => props.active ? theme.colors.primary : (props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border)};
  border-radius: ${theme.radius.md};
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${props => props.active ? `linear-gradient(135deg, ${theme.colors.primary}30 0%, ${theme.colors.accent}15 100%)` : (props.isDarkMode ? theme.colors.dark.surfaceHover : theme.colors.light.surfaceHover)};
    transform: translateY(-1px);
    box-shadow: ${theme.shadows.md};
  }
`;

const SendButton = styled(Button)`
  min-width: 7.5rem;
  height: 3rem;
  font-size: 1rem;
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
  background: ${props => props.isDarkMode ? `linear-gradient(135deg, ${theme.colors.dark.surface} 0%, ${theme.colors.dark.background} 100%)` : `linear-gradient(135deg, ${theme.colors.light.surface} 0%, ${theme.colors.light.background} 100%)`};
  border: 1px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  border-radius: ${theme.radius.lg};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  text-align: center;
  min-width: 9.375rem;
  
  &:hover {
    transform: translateY(-0.25rem);
    box-shadow: ${theme.shadows.lg}, 0 0 15px ${theme.colors.primary}50;
    border-color: ${theme.colors.primary};
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
  .number { font-size: 2rem; font-weight: 800; color: ${theme.colors.primary}; }
  .label { font-size: 0.75rem; color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted}; margin-top: ${theme.spacing.xs_rem}; }
`;

export default function Home() {
  const [messageText, setMessageText] = useState('');
  const [thinkingMode, setThinkingMode] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const accessToken = useSelector(state => state.accessToken);
  const isDarkMode = useSelector(state => state.isDarkMode);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const createThread = async () => {
    if (messageText.length === 0) return;
    const data = {task: messageText, extended_thinking_mode: thinkingMode};
    setMessageText('');
    dispatch(setLoadingDialog(true));
    try {
      const response = await axios.post('/threads', data, {
        headers: { 'Authorization': 'Bearer ' + accessToken }
      });
      dispatch(setLoadingDialog(false));
      if (response.data.type === 'desktop_task') {
        setThinkingMode(thinkingMode || response.data.is_extended_thinking_mode_requested);
        window.electronAPI.setLastThinkingModeValue((thinkingMode || response.data.is_extended_thinking_mode_requested).toString());
        window.electronAPI.launchAIAgent(
          process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS,
          response.data.thread_id
        );
      }
      navigate('/threads/' + response.data.thread_id);
    } catch (error) {
      dispatch(setLoadingDialog(false));
      dispatch(setError(true, constants.GENERAL_ERROR));
      setTimeout(() => dispatch(setError(false, '')), 3000);
    }
  };

  useEffect(() => {
    const asyncTask = async () => {
      const lastThinkingModeValue = await window.electronAPI.getLastThinkingModeValue();
      setThinkingMode(lastThinkingModeValue === 'true');
    };
    asyncTask();
  }, []);

  const quickActions = [
    { icon: <FaBolt />, title: "Quick Task", action: () => setMessageText("Organize my desktop files") },
    { icon: <MdLightbulb />, title: "Smart Suggestion", action: () => setMessageText("Suggest productivity improvements") },
    { icon: <MdRocket />, title: "Power User", action: () => setMessageText("System optimization routine") }
  ];

  return (
    <HomeContainer isDarkMode={isDarkMode}>
      <WelcomeSection isDarkMode={isDarkMode}>
        <div className="engine-badge">Elite Engine v2.2 Active</div>
        <h1><FaRobot style={{ marginRight: '16px' }} />01Agent</h1>
        <p>Lightning-fast AI desktop assistant</p>
      </WelcomeSection>

      <TaskCard isDarkMode={isDarkMode} hover glow>
        <TaskInput isDarkMode={isDarkMode} placeholder="What should I do?" value={messageText} onChange={(e) => setMessageText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && createThread()} />
        <ControlsRow>
          <ModeToggles>
            <ModeToggle active={thinkingMode} isDarkMode={isDarkMode} onClick={() => setThinkingMode(!thinkingMode)}><GiBrain /> Deep Thinking</ModeToggle>
          </ModeToggles>
          <SendButton variant="primary" size="lg" disabled={messageText.length === 0} onClick={createThread} isDarkMode={isDarkMode}>Execute Task</SendButton>
        </ControlsRow>
      </TaskCard>

      <QuickActions>
        {quickActions.map((action, index) => (
          <QuickActionCard key={index} isDarkMode={isDarkMode} onClick={action.action}>
            <div className="icon" style={{color: theme.colors.primary, fontSize: '1.5rem'}}>{action.icon}</div>
            <div className="title" style={{fontWeight: 600}}>{action.title}</div>
          </QuickActionCard>
        ))}
      </QuickActions>

      <StatsRow>
        <StatItem isDarkMode={isDarkMode}><div className="number">80%</div><div className="label">Faster</div></StatItem>
        <StatItem isDarkMode={isDarkMode}><div className="number">95%</div><div className="label">Success</div></StatItem>
      </StatsRow>
    </HomeContainer>
  );
}
