import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Login from './views/Login';
import Home from './views/Home';
import Thread from './views/Thread';
import Dashboard from './views/Dashboard';
import Performance from './views/Performance';
import AgentStatus from './views/AgentStatus';
import Settings from './views/Settings';
import ModernSidebar from './layouts/ModernSidebar';
import FullLoading from './components/FullLoading';
import ErrorBoundary from './components/ErrorHandling/ErrorBoundary';

const App = () => {
  const accessToken = useSelector(state => state.accessToken);
  const loadingDialog = useSelector(state => state.loadingDialog);

  if (!accessToken) {
    return (
      <Routes>
        <Route path="*" element={<Login />} />
      </Routes>
    );
  }

  return (
    <ErrorBoundary>
      <div className="flex h-screen w-screen overflow-hidden bg-[#0a0f1d] font-sans selection:bg-emerald-500/30 selection:text-emerald-200">
        <ModernSidebar />
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/threads/:tid" element={<Thread />} />
            <Route path="/threads" element={<Navigate to="/" replace />} />
            <Route path="/performance" element={<Performance />} />
            <Route path="/status" element={<AgentStatus />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
        {loadingDialog && <FullLoading />}
      </div>
    </ErrorBoundary>
  );
};

export default App;
