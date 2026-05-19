import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setAccessToken, setUser } from '../store';

function SimpleLogin() {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleDemoLogin = () => {
    // Set demo user and token
    dispatch(setAccessToken('demo-token-123'));
    dispatch(setUser({
      id: 'demo-user',
      name: 'Demo User',
      email: 'demo@01agent.com'
    }));
    
    // Navigate to home
    navigate('/');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-[#1e3c72] to-[#2a5298] text-white p-8">
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-12 text-center shadow-[0_8px_32px_rgba(0,0,0,0.3)] border border-white/20 w-full max-w-[400px]">
        <h1 className="text-4xl mb-4 bg-gradient-to-tr from-[#00ff88] to-[#00ccff] bg-clip-text text-transparent">
          🤖 01Agent
        </h1>
        <p className="text-lg mb-8 opacity-90">
          AI Desktop Agent
        </p>
        
        <button
          onClick={handleDemoLogin}
          className="bg-gradient-to-tr from-[#00ff88] to-[#00ccff] text-[#1a1a1a] border-none py-4 px-8 rounded-lg text-lg font-bold cursor-pointer transition-all duration-300 ease-in-out m-2 hover:-translate-y-0.5 hover:shadow-[0_8px_25px_rgba(0,255,136,0.3)]"
        >
          🚀 Enter Demo Mode
        </button>
        
        <div className="mt-8 text-sm opacity-80 leading-relaxed text-left inline-block">
          <p className="mb-2">✨ <strong>Demo Mode Features:</strong></p>
          <p className="ml-2">• Full dashboard access</p>
          <p className="ml-2">• Agent control interface</p>
          <p className="ml-2">• Performance monitoring</p>
          <p className="ml-2">• Settings configuration</p>
          <p className="ml-2">• Task management</p>
        </div>
      </div>
    </div>
  );
}

export default SimpleLogin;