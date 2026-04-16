import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import _01agent_logo_ic_only_white from '../assets/01agent_logo_ic_only_white.png';
import _01agent_logo_ic_only from '../assets/01agent_logo_ic_only.png';
import { AvatarButton, IconButton } from '../components/Elements/Button';
import { useSelector } from 'react-redux';
import axios from '../utils/axios';
import { FaStopCircle, FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa';
import constants from '../utils/constants';
import { MdOutlineSchedule } from 'react-icons/md';
import { GiBrain } from 'react-icons/gi';

const Container = styled.div`
  background: transparent;
  padding: 0px 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100vh;
  width: 100%;
  transition: height 0.3s ease;
`;

const Input = styled.input`
  flex: 1;
  border: 1px solid var(--border-dark); /* Sci-fi border */
  background: var(--surface-dark); /* Sci-fi background */
  color: var(--text-light); /* Sci-fi text color */
  font-size: 14px;
  outline: none;
  border-radius: 4px; /* Sharper corners */

  &:focus {
    outline: 1px solid var(--sci-fi-green); /* Sci-fi green focus outline */
  }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const Spinner = styled.div`
  margin-left: 8px;
  width: 21px;
  height: 21px;
  border: 2px solid var(--sci-fi-green); /* Sci-fi green spinner */
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

const SuggestionsPanel = styled.div`
  margin-top: 5px;
  background-color: var(--surface-dark); /* Sci-fi background */
  border-radius: 4px; /* Sharper corners */
  padding: 10px;
  flex: 1;
  overflow-y: auto;
  border: 1px solid var(--border-dark); /* Sci-fi border */
`;

const SuggestionItem = styled.div`
  padding: 8px;
  margin-bottom: 6px;
  background: var(--background-dark); /* Sci-fi background */
  border-radius: 4px; /* Sharper corners */
  color: var(--text-light); /* Sci-fi text color */
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s; /* Add border-color to transition */
  border: 1px solid transparent; /* Default transparent border */

  &:hover {
    background: var(--surface-dark); /* Hover background */
    border-color: var(--sci-fi-green); /* Sci-fi green border on hover */
  }
`;

const shimmer = keyframes`
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
`;

const SkeletonItem = styled.div`
  height: 36px;
  margin-bottom: 6px;
  border-radius: 4px; /* Sharper corners */
  background: linear-gradient(90deg,rgba(var(--text-light), 0.07) 25%, rgba(var(--text-light), 0.15) 50%,rgba(var(--text-light), 0.07) 75%); /* Sci-fi gradient */
  background-size: 200px 100%;
  animation: ${shimmer} 1.2s infinite;
`;

const ToggleContainer = styled.div`
  display: flex;
  align-items: center;
`;

const ModeToggle = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: ${props => (props.active ? 'var(--surface-dark)' : 'transparent')}; /* Active state uses surface dark */
  color: ${props => props.active ? 'var(--sci-fi-green)' : 'var(--text-light)'}; /* Active state uses sci-fi green */
  border: ${props => props.active ? '1px solid var(--sci-fi-green)' : '1px solid var(--border-dark)'}; /* Active state uses sci-fi green border */
  border-radius: 4px; /* Sharper corners */
  padding: 4px 10px;
  font-size: 11.5px;
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease; /* Add color and border-color to transition */
  cursor: pointer;

  &:hover {
    background-color: var(--surface-dark); /* Hover uses surface dark */
    box-shadow: 0 0 8px var(--sci-fi-green); /* Sci-fi green glow on hover */
  }

  svg {
    font-size: 15px;
    color: var(--sci-fi-green); /* Sci-fi green icon color */
  }
`;

const ActionMarker = styled.div`
  position: absolute;
  width: 40px;
  height: 40px;
  border: 3px solid var(--sci-fi-green);
  border-radius: 50%;
  pointer-events: none;
  transform: translate(-50%, -50%);
  z-index: 9999;
  animation: ${keyframes`
    0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
  `} 0.8s ease-out forwards;
`;

const FeedbackText = styled.div`
  position: absolute;
  bottom: 80px;
  right: 20px;
  background: var(--surface-dark);
  color: var(--sci-fi-green);
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid var(--sci-fi-green);
  font-family: monospace;
  font-size: 14px;
  pointer-events: none;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
`;

export default function Overlay() {
  const [expanded, setExpanded] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [messageText, setMessageText] = useState('');
  const [loading, setLoading] = useState(false);
  const [runningThreadId, setRunningThreadId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [backgroundMode, setBackgroundMode] = useState(false);
  const [thinkingMode, setThinkingMode] = useState(false);
  const [activeAction, setActiveAction] = useState(null);
  const [isListening, setIsListening] = useState(false);

  const accessToken = useSelector(state => state.accessToken);
  const isDarkMode = useSelector(state => state.isDarkMode);

  const executeTask = () => {
    if (loading) {
      return;
    }
    createThread();
  };

  const executeSuggestion = (prompt) => {
    if (loading) return;

    window.electronAPI.expandOverlay(false);
    setShowSuggestions(false);
    createThread(prompt);
  };

  const toggleOverlay = async () => {
    if (!expanded) {
      if (runningThreadId === null) {
        window.electronAPI.expandOverlay(true);
        setExpanded(true);
        setShowSuggestions(true);
        if (suggestions.length === 0) {
          getSuggestions();
        }
      } else {
        window.electronAPI.expandOverlay(false);
        setExpanded(true);
      }
    } else {
      window.electronAPI.minimizeOverlay();
      setExpanded(false);
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const getSuggestions = async () => {
    const suggestedTasks = await window.electronAPI.getSuggestions(
      process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS,
    );
    setSuggestions(suggestedTasks.suggestions);
  };

  const cancelRunningTask = (tid) => {
    setLoading(true);
    axios.post(`/threads/${tid}/cancel_task`, {}, {
      headers: {
        'Authorization': 'Bearer ' + accessToken,
      }
    }).then((response) => {
      setLoading(false);
      window.electronAPI.stopAIAgent();
      setRunningThreadId(null);
    }).catch((error) => {
      setLoading(false);
      if (error.response?.status === constants.status.UNAUTHORIZED) {
        window.location.reload();
      }
    });
  };

  const createThread = async (prompt = null) => {
    if (messageText.length === 0 && prompt === null) {
      return;
    }

    const data = {task: prompt !== null ? prompt : messageText, background_mode: backgroundMode, extended_thinking_mode: thinkingMode};
    setMessageText('');
    setLoading(true);
    axios.post('/threads', data, {
      headers: {
        'Authorization': 'Bearer ' + accessToken,
      }
    }).then(async (response) => {
      setLoading(false);
      if (response.data.type === 'desktop_task') {
        if (!backgroundMode && response.data.is_background_mode_requested) {
          const ready = await window.electronAPI.isBackgroundModeReady();
          if (!ready) {
            cancelRunningTask();
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
        setRunningThreadId(response.data.thread_id);
      }
    }).catch((error) => {
      setLoading(false);
      if (error.response?.status === constants.status.UNAUTHORIZED) {
        window.location.reload();
      }
    });
  };

  const toggleVoice = () => {
    if (isListening) {
      setIsListening(false);
    } else {
      startListening();
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = (e) => {
      console.error(e);
      setIsListening(false);
    };
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setMessageText(transcript);
    };

    recognition.start();
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
        window.electronAPI.expandOverlay(false);
        setExpanded(true);
        setRunningThreadId(threadId);
        setShowSuggestions(false);
      });
    }
  }, []);

  useEffect(() => {
    if (window.electronAPI?.onAgentAction) {
      window.electronAPI.onAgentAction((data) => {
        setActiveAction(data);
        setTimeout(() => setActiveAction(null), 2000);
      });
    }
  }, []);

  useEffect(() => {
    if (window.electronAPI?.onAIAgentExit) {
      window.electronAPI.onAIAgentExit(() => {
        setRunningThreadId(null);
        window.electronAPI.expandOverlay(true);
        setShowSuggestions(true);
        setSuggestions([]);
        getSuggestions();
      });
    }
  }, []);

  useEffect(() => {
    const asyncTask = async () => {
      const lastBackgroundModeValue = await window.electronAPI.getLastBackgroundModeValue();
      setBackgroundMode(lastBackgroundModeValue === 'true');
    };
    asyncTask();
  }, []);

  useEffect(() => {
    const asyncTask = async () => {
      const lastThinkingModeValue = await window.electronAPI.getLastThinkingModeValue();
      setThinkingMode(lastThinkingModeValue === 'true');
    };
    asyncTask();
  }, []);

  return (
    <Container>
      {activeAction && activeAction.params?.x && activeAction.params?.y && (
        <ActionMarker
          key={Date.now()}
          style={{ left: activeAction.params.x, top: activeAction.params.y }}
        />
      )}

      {activeAction && (
        <FeedbackText>
          ⚡ {activeAction.action.replace('_', ' ')}: {activeAction.params?.text || ''}
        </FeedbackText>
      )}

      <div style={{display: 'flex', alignItems: 'center', width: '100%', height: '60px', position: 'absolute', bottom: 0, right: 0, background: expanded ? 'transparent' : 'transparent'}}>
        <AvatarButton color='transparent' onClick={() => toggleOverlay()}>
          <img
            src={isDarkMode ? _01agent_logo_ic_only_white : _01agent_logo_ic_only}
            alt='01Agent'
            height={46}
            style={{userSelect: 'none', pointerEvents: 'none'}}
          />
        </AvatarButton>
        {expanded && (
          <>
            <div style={{width: '10px'}} />
            <Input
              value={messageText}
              isDarkMode={isDarkMode}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Ask 01Agent..."
              onKeyDown={(e) => e.key === 'Enter' && executeTask()}
            />
            {!loading && runningThreadId === null && (
              <> 
                <div style={{width: '5px'}} />
                <ToggleContainer>
                  <ModeToggle
                    active={backgroundMode}
                    isDarkMode={isDarkMode}
                    onClick={() => onBGModeToggleChange(!backgroundMode)}
                  >
                    <MdOutlineSchedule />
                  </ModeToggle>
                </ToggleContainer>
                <div style={{width: '5px'}} />
                <ToggleContainer>
                  <ModeToggle
                    active={thinkingMode}
                    isDarkMode={isDarkMode}
                    onClick={() => setThinkingMode(!thinkingMode)}
                  >
                    <GiBrain />
                  </ModeToggle>
                </ToggleContainer>
                <div style={{width: '5px'}} />
                <ToggleContainer>
                  <ModeToggle
                    active={isListening}
                    isDarkMode={isDarkMode}
                    onClick={toggleVoice}
                  >
                    {isListening ? <FaMicrophoneSlash /> : <FaMicrophone />}
                  </ModeToggle>
                </ToggleContainer>
              </>
            )}
            {(loading || runningThreadId !== null) && <Spinner isDarkMode={isDarkMode} />}
            <div style={{width: '5px'}} />
            {
            runningThreadId !== null && <>
                <IconButton iconSize='21px' color={'var(--sci-fi-green)'} onClick={() => cancelRunningTask(runningThreadId)}
                  disabled={loading}>
                  <FaStopCircle />
                </IconButton>
              </>
            }
          </>
        )}
      </div>
      {expanded && showSuggestions && (
        <SuggestionsPanel isDarkMode={isDarkMode}>
          {suggestions.length === 0
            ? Array.from({ length: 7 }).map((_, idx) => (
                <SkeletonItem isDarkMode={isDarkMode} key={idx} />
              ))
            : suggestions.map((s, idx) => (
                <SuggestionItem
                  key={idx}
                  isDarkMode={isDarkMode}
                  onClick={() => executeSuggestion(s.ai_prompt)}
                >
                  {s.title}
                </SuggestionItem>
              ))}
        </SuggestionsPanel>
      )}
    </Container>
  );
}