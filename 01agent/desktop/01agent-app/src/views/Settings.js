import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import {
  SidePanelContent,
  SidePanelHeader,
  SidePanelTitle,
  SidePanelBody,
  Card,
  CardHeader,
  CardContent,
  QuickActionButton,
  Badge,
  ProgressBar
} from '../layouts/ModernContainers';

const Settings = () => {
  const isDarkMode = useSelector(state => state.isDarkMode);
  
  const [settings, setSettings] = useState({
    execution: {
      strategy: 'speed_priority',
      timeout: 30,
      retryAttempts: 3,
      adaptiveStrategy: true
    },
    performance: {
      screenshotScale: 0.7,
      cacheTimeout: 1.5,
      maxConcurrentTasks: 8,
      fastMode: true,
      memoryCleanupThreshold: 85
    },
    ui: {
      detectionConfidence: 0.8,
      clickDelay: 0.01,
      typeInterval: 0.005,
      screenshotQuality: 85
    },
    system: {
      optimizeForSystem: true,
      useHardwareAcceleration: true,
      tempCleanupEnabled: true,
      logLevel: 'INFO'
    }
  });

  const [isLoading, setIsLoading] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);

  useEffect(() => {
    // Load settings from backend or electron store
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      // This would typically load from your backend or electron store
      // For now, we'll use the default settings
      console.log('Loading settings...');
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async () => {
    setIsLoading(true);
    try {
      // This would typically save to your backend or electron store
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      setLastSaved(new Date());
      console.log('Settings saved:', settings);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetToDefaults = () => {
    setSettings({
      execution: {
        strategy: 'speed_priority',
        timeout: 30,
        retryAttempts: 3,
        adaptiveStrategy: true
      },
      performance: {
        screenshotScale: 0.7,
        cacheTimeout: 1.5,
        maxConcurrentTasks: 8,
        fastMode: true,
        memoryCleanupThreshold: 85
      },
      ui: {
        detectionConfidence: 0.8,
        clickDelay: 0.01,
        typeInterval: 0.005,
        screenshotQuality: 85
      },
      system: {
        optimizeForSystem: true,
        useHardwareAcceleration: true,
        tempCleanupEnabled: true,
        logLevel: 'INFO'
      }
    });
  };

  const optimizeForSpeed = () => {
    setSettings(prev => ({
      ...prev,
      execution: {
        ...prev.execution,
        strategy: 'speed_priority',
        timeout: 20,
        retryAttempts: 2
      },
      performance: {
        ...prev.performance,
        screenshotScale: 0.6,
        cacheTimeout: 1.0,
        fastMode: true
      },
      ui: {
        ...prev.ui,
        detectionConfidence: 0.75,
        clickDelay: 0.005,
        typeInterval: 0.003,
        screenshotQuality: 75
      }
    }));
  };

  const optimizeForReliability = () => {
    setSettings(prev => ({
      ...prev,
      execution: {
        ...prev.execution,
        strategy: 'reliability_priority',
        timeout: 45,
        retryAttempts: 5
      },
      performance: {
        ...prev.performance,
        screenshotScale: 0.8,
        cacheTimeout: 2.0,
        fastMode: false
      },
      ui: {
        ...prev.ui,
        detectionConfidence: 0.9,
        clickDelay: 0.02,
        typeInterval: 0.01,
        screenshotQuality: 95
      }
    }));
  };

  const handleInputChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const SettingItem = ({ label, value, onChange, type = 'text', min, max, step, options }) => (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      marginBottom: '12px',
      padding: '8px 0'
    }}>
      <label style={{ 
        fontSize: '14px', 
        color: isDarkMode ? '#e1e4e8' : '#586069',
        flex: 1
      }}>
        {label}
      </label>
      {type === 'select' ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          style={{
            padding: '4px 8px',
            borderRadius: '4px',
            border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
            background: isDarkMode ? '#2a2a2a' : '#ffffff',
            color: isDarkMode ? '#ffffff' : '#24292e',
            fontSize: '13px',
            minWidth: '120px'
          }}
        >
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : type === 'checkbox' ? (
        <input
          type="checkbox"
          checked={value}
          onChange={(e) => onChange(e.target.checked)}
          style={{ transform: 'scale(1.2)' }}
        />
      ) : type === 'range' ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '120px' }}>
          <input
            type="range"
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            style={{ flex: 1 }}
          />
          <span style={{ 
            fontSize: '12px', 
            color: isDarkMode ? '#9ca3af' : '#6b7280',
            minWidth: '40px',
            textAlign: 'right'
          }}>
            {typeof value === 'number' ? value.toFixed(step < 1 ? 2 : 0) : value}
          </span>
        </div>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(type === 'number' ? parseFloat(e.target.value) : e.target.value)}
          min={min}
          max={max}
          step={step}
          style={{
            padding: '4px 8px',
            borderRadius: '4px',
            border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
            background: isDarkMode ? '#2a2a2a' : '#ffffff',
            color: isDarkMode ? '#ffffff' : '#24292e',
            fontSize: '13px',
            minWidth: '80px',
            textAlign: 'right'
          }}
        />
      )}
    </div>
  );

  return (
    <SidePanelContent>
      <SidePanelHeader isDarkMode={isDarkMode}>
        <SidePanelTitle isDarkMode={isDarkMode}>
          ⚙️ Settings
        </SidePanelTitle>
        <div style={{ display: 'flex', gap: '8px' }}>
          {lastSaved && (
            <Badge variant="success" isDarkMode={isDarkMode}>
              Saved {lastSaved.toLocaleTimeString()}
            </Badge>
          )}
        </div>
      </SidePanelHeader>

      <SidePanelBody>
        <div style={{ padding: '20px', maxWidth: '800px' }}>
          
          {/* Quick Optimization */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Quick Optimization</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={optimizeForSpeed}
                >
                  🚀 Optimize for Speed
                </QuickActionButton>
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={optimizeForReliability}
                >
                  🛡️ Optimize for Reliability
                </QuickActionButton>
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={resetToDefaults}
                >
                  🔄 Reset to Defaults
                </QuickActionButton>
              </div>
            </CardContent>
          </Card>

          {/* Execution Settings */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Execution Settings</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <SettingItem
                label="Execution Strategy"
                value={settings.execution.strategy}
                onChange={(value) => handleInputChange('execution', 'strategy', value)}
                type="select"
                options={[
                  { value: 'speed_priority', label: 'Speed Priority' },
                  { value: 'reliability_priority', label: 'Reliability Priority' },
                  { value: 'background_priority', label: 'Background Priority' },
                  { value: 'gui_priority', label: 'GUI Priority' }
                ]}
              />
              <SettingItem
                label="Timeout (seconds)"
                value={settings.execution.timeout}
                onChange={(value) => handleInputChange('execution', 'timeout', value)}
                type="number"
                min={5}
                max={120}
              />
              <SettingItem
                label="Retry Attempts"
                value={settings.execution.retryAttempts}
                onChange={(value) => handleInputChange('execution', 'retryAttempts', value)}
                type="number"
                min={1}
                max={10}
              />
              <SettingItem
                label="Adaptive Strategy"
                value={settings.execution.adaptiveStrategy}
                onChange={(value) => handleInputChange('execution', 'adaptiveStrategy', value)}
                type="checkbox"
              />
            </CardContent>
          </Card>

          {/* Performance Settings */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Performance Settings</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <SettingItem
                label="Screenshot Scale"
                value={settings.performance.screenshotScale}
                onChange={(value) => handleInputChange('performance', 'screenshotScale', value)}
                type="range"
                min={0.3}
                max={1.0}
                step={0.1}
              />
              <SettingItem
                label="Cache Timeout (seconds)"
                value={settings.performance.cacheTimeout}
                onChange={(value) => handleInputChange('performance', 'cacheTimeout', value)}
                type="range"
                min={0.5}
                max={5.0}
                step={0.1}
              />
              <SettingItem
                label="Max Concurrent Tasks"
                value={settings.performance.maxConcurrentTasks}
                onChange={(value) => handleInputChange('performance', 'maxConcurrentTasks', value)}
                type="number"
                min={1}
                max={20}
              />
              <SettingItem
                label="Fast Mode"
                value={settings.performance.fastMode}
                onChange={(value) => handleInputChange('performance', 'fastMode', value)}
                type="checkbox"
              />
              <SettingItem
                label="Memory Cleanup Threshold (%)"
                value={settings.performance.memoryCleanupThreshold}
                onChange={(value) => handleInputChange('performance', 'memoryCleanupThreshold', value)}
                type="range"
                min={50}
                max={95}
                step={5}
              />
            </CardContent>
          </Card>

          {/* UI Settings */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>UI Detection Settings</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <SettingItem
                label="Detection Confidence"
                value={settings.ui.detectionConfidence}
                onChange={(value) => handleInputChange('ui', 'detectionConfidence', value)}
                type="range"
                min={0.5}
                max={1.0}
                step={0.05}
              />
              <SettingItem
                label="Click Delay (seconds)"
                value={settings.ui.clickDelay}
                onChange={(value) => handleInputChange('ui', 'clickDelay', value)}
                type="range"
                min={0.001}
                max={0.1}
                step={0.001}
              />
              <SettingItem
                label="Type Interval (seconds)"
                value={settings.ui.typeInterval}
                onChange={(value) => handleInputChange('ui', 'typeInterval', value)}
                type="range"
                min={0.001}
                max={0.05}
                step={0.001}
              />
              <SettingItem
                label="Screenshot Quality (%)"
                value={settings.ui.screenshotQuality}
                onChange={(value) => handleInputChange('ui', 'screenshotQuality', value)}
                type="range"
                min={50}
                max={100}
                step={5}
              />
            </CardContent>
          </Card>

          {/* System Settings */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>System Settings</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <SettingItem
                label="Optimize for System"
                value={settings.system.optimizeForSystem}
                onChange={(value) => handleInputChange('system', 'optimizeForSystem', value)}
                type="checkbox"
              />
              <SettingItem
                label="Hardware Acceleration"
                value={settings.system.useHardwareAcceleration}
                onChange={(value) => handleInputChange('system', 'useHardwareAcceleration', value)}
                type="checkbox"
              />
              <SettingItem
                label="Temp Cleanup Enabled"
                value={settings.system.tempCleanupEnabled}
                onChange={(value) => handleInputChange('system', 'tempCleanupEnabled', value)}
                type="checkbox"
              />
              <SettingItem
                label="Log Level"
                value={settings.system.logLevel}
                onChange={(value) => handleInputChange('system', 'logLevel', value)}
                type="select"
                options={[
                  { value: 'DEBUG', label: 'Debug' },
                  { value: 'INFO', label: 'Info' },
                  { value: 'WARNING', label: 'Warning' },
                  { value: 'ERROR', label: 'Error' }
                ]}
              />
            </CardContent>
          </Card>

          {/* Save Button */}
          <div style={{ 
            position: 'sticky', 
            bottom: '20px', 
            background: isDarkMode ? '#1a1a1a' : '#ffffff',
            padding: '16px 0',
            borderTop: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
            marginTop: '20px'
          }}>
            <QuickActionButton
              primary
              isDarkMode={isDarkMode}
              onClick={saveSettings}
              disabled={isLoading}
            >
              {isLoading ? '💾 Saving...' : '💾 Save Settings'}
            </QuickActionButton>
          </div>
        </div>
      </SidePanelBody>
    </SidePanelContent>
  );
};

export default Settings;