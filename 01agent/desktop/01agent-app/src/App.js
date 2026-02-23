import React, { useState, lazy, Suspense } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './store';
import './App.css';

// Lazy load components
const LazyDashboard = lazy(() => import('./views/Dashboard'));
const LazySimpleLogin = lazy(() => import('./views/SimpleLogin'));

import ErrorBoundary from './components/ErrorHandling/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <Router>
          <Suspense fallback={<div>Loading...</div>}>
            <Routes>
              <Route path="/" element={<LazySimpleLogin />} />
              <Route path="/dashboard" element={<LazyDashboard />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </Router>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;