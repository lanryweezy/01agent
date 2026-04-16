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
  Badge
} from '../layouts/ModernContainers';

const Settings = () => {
  const isDarkMode = useSelector(state => state.isDarkMode);
  
  const [settings, setSettings] = useState({
    execution: {
      strategy: 'vision_centric',
      timeout: 30,
      retryAttempts: 3
    },
    ui: {
      screenshotQuality: 75,
      typeInterval: 0.01,
      clickDelay: 0.05
    },
    system: {
      logLevel: 'INFO',
      autoStart: true
    }
  });

  const [isLoading, setIsLoading] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);

  const saveSettings = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      setLastSaved(new Date());
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsLoading(false);
    }
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
            fontSize: '13px'
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
        />
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
            width: '80px',
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
        {lastSaved && (
          <Badge variant="success" isDarkMode={isDarkMode}>
            Saved {lastSaved.toLocaleTimeString()}
          </Badge>
        )}
      </SidePanelHeader>

      <SidePanelBody>
        <div style={{ padding: '20px', maxWidth: '600px' }}>
          
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Vision & Execution</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <SettingItem
                label="Screenshot Quality (%)"
                value={settings.ui.screenshotQuality}
                onChange={(v) => handleInputChange('ui', 'screenshotQuality', v)}
                type="number"
                min={50}
                max={100}
              />
              <SettingItem
                label="Action Timeout (s)"
                value={settings.execution.timeout}
                onChange={(v) => handleInputChange('execution', 'timeout', v)}
                type="number"
              />
              <SettingItem
                label="Retry Attempts"
                value={settings.execution.retryAttempts}
                onChange={(v) => handleInputChange('execution', 'retryAttempts', v)}
                type="number"
              />
            </CardContent>
          </Card>

          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>System</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <SettingItem
                label="Log Level"
                value={settings.system.logLevel}
                onChange={(v) => handleInputChange('system', 'logLevel', v)}
                type="select"
                options={[
                  { value: 'DEBUG', label: 'Debug' },
                  { value: 'INFO', label: 'Info' },
                  { value: 'ERROR', label: 'Error' }
                ]}
              />
              <SettingItem
                label="Auto-start Agent"
                value={settings.system.autoStart}
                onChange={(v) => handleInputChange('system', 'autoStart', v)}
                type="checkbox"
              />
            </CardContent>
          </Card>

          <div style={{ marginTop: '20px' }}>
            <QuickActionButton
              primary
              isDarkMode={isDarkMode}
              onClick={saveSettings}
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : '💾 Save Settings'}
            </QuickActionButton>
          </div>
        </div>
      </SidePanelBody>
    </SidePanelContent>
  );
};

export default Settings;
