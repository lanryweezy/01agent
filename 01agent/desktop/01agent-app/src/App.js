import React, { lazy, Suspense } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './store';
import './App.css';

import MainLayout from './layouts/MainLayout';
import ErrorBoundary from './components/ErrorHandling/ErrorBoundary';
import FullLoading from './components/FullLoading';

// Lazy load views
const Home = lazy(() => import('./views/Home'));
const Thread = lazy(() => import('./views/Thread'));
const Settings = lazy(() => import('./views/Settings'));
const Performance = lazy(() => import('./views/Performance'));
const AgentStatus = lazy(() => import('./views/AgentStatus'));
const Marketplace = lazy(() => import('./views/Marketplace'));
const SimpleLogin = lazy(() => import('./views/SimpleLogin'));

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <Router>
          <Suspense fallback={<FullLoading />}>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<SimpleLogin />} />

              {/* Protected Routes (Wrapped in MainLayout) */}
              <Route path="/" element={
                <MainLayout>
                  <Home />
                </MainLayout>
              } />
              <Route path="/threads/:tid" element={
                <MainLayout>
                  <Thread />
                </MainLayout>
              } />
              <Route path="/threads" element={
                <MainLayout>
                  <Navigate to="/" replace />
                </MainLayout>
              } />
              <Route path="/settings" element={
                <MainLayout>
                  <Settings />
                </MainLayout>
              } />
              <Route path="/performance" element={
                <MainLayout>
                  <Performance />
                </MainLayout>
              } />
              <Route path="/status" element={
                <MainLayout>
                  <AgentStatus />
                </MainLayout>
              } />
              <Route path="/marketplace" element={
                <MainLayout>
                  <Marketplace />
                </MainLayout>
              } />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </Router>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;
