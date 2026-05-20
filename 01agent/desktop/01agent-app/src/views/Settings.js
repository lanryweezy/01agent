import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import {
  Settings as SettingsIcon,
  Save,
  Shield,
  Monitor,
  Cpu,
  Database,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

const SettingItem = ({ label, value, onChange, type = 'text', min, max, step, options }) => (
  <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
    <div className="flex flex-col">
      <span className="text-sm font-medium text-slate-300">{label}</span>
    </div>
    <div className="flex items-center gap-3">
      {type === 'select' ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:border-emerald-500/50 outline-none transition-colors"
        >
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : type === 'checkbox' ? (
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => onChange(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-9 h-5 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-400 after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-500 peer-checked:after:bg-white"></div>
        </label>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(type === 'number' ? parseFloat(e.target.value) : e.target.value)}
          min={min}
          max={max}
          step={step}
          className="bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white text-right focus:border-emerald-500/50 outline-none transition-colors w-24 font-mono"
        />
      )}
    </div>
  </div>
);

const Settings = () => {
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
  const [showSavedToast, setShowSavedToast] = useState(false);

  const saveSettings = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      setShowSavedToast(true);
      setTimeout(() => setShowSavedToast(false), 3000);
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

  return (
    <div className="flex-1 overflow-y-auto bg-[#0a0f1d] p-8">
      <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

        {/* Header */}
        <div className="flex items-center justify-between pb-6 border-b border-white/10">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <SettingsIcon className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Configuration</h1>
              <p className="text-slate-400 text-sm">Fine-tune the agent performance and behavior.</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {showSavedToast && (
              <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium animate-in fade-in slide-in-from-right-4">
                <CheckCircle2 className="w-4 h-4" />
                Settings Synchronized
              </div>
            )}
            <button
              onClick={saveSettings}
              disabled={isLoading}
              className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-700 text-slate-900 px-6 py-2.5 rounded-xl font-bold transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-emerald-500/20"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-slate-900/30 border-t-slate-900 rounded-full animate-spin" />
              ) : (
                <Save className="w-5 h-5" />
              )}
              Save Changes
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Vision & Execution */}
          <div className="bg-white/[0.03] border border-white/5 rounded-2xl p-6 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                <Monitor className="w-5 h-5 text-cyan-400" />
              </div>
              <h3 className="font-bold text-white uppercase tracking-wider text-sm">Vision & Execution</h3>
            </div>

            <div className="space-y-1">
              <SettingItem
                label="Screenshot Quality (%)"
                value={settings.ui.screenshotQuality}
                onChange={(v) => handleInputChange('ui', 'screenshotQuality', v)}
                type="number"
                min={50}
                max={100}
              />
              <SettingItem
                label="Action Timeout (seconds)"
                value={settings.execution.timeout}
                onChange={(v) => handleInputChange('execution', 'timeout', v)}
                type="number"
                min={1}
              />
              <SettingItem
                label="Max Retry Attempts"
                value={settings.execution.retryAttempts}
                onChange={(v) => handleInputChange('execution', 'retryAttempts', v)}
                type="number"
                min={0}
              />
            </div>
          </div>

          {/* System Security */}
          <div className="bg-white/[0.03] border border-white/5 rounded-2xl p-6 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                <Shield className="w-5 h-5 text-emerald-400" />
              </div>
              <h3 className="font-bold text-white uppercase tracking-wider text-sm">System & Security</h3>
            </div>

            <div className="space-y-1">
              <SettingItem
                label="Diagnostic Log Level"
                value={settings.system.logLevel}
                onChange={(v) => handleInputChange('system', 'logLevel', v)}
                type="select"
                options={[
                  { value: 'DEBUG', label: 'Detailed (Debug)' },
                  { value: 'INFO', label: 'Standard (Info)' },
                  { value: 'ERROR', label: 'Minimal (Error)' }
                ]}
              />
              <SettingItem
                label="Initialize on System Start"
                value={settings.system.autoStart}
                onChange={(v) => handleInputChange('system', 'autoStart', v)}
                type="checkbox"
              />
            </div>
          </div>

          {/* Expert Mode */}
          <div className="bg-white/[0.03] border border-white/5 rounded-2xl p-6 backdrop-blur-sm md:col-span-2">
             <div className="flex items-center gap-3 mb-6 text-amber-400/50">
               <AlertCircle className="w-5 h-5" />
               <span className="text-xs font-bold uppercase tracking-[0.2em]">Expert Action Delays</span>
             </div>
             <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-12">
                <SettingItem
                  label="Keystroke Interval (s)"
                  value={settings.ui.typeInterval}
                  onChange={(v) => handleInputChange('ui', 'typeInterval', v)}
                  type="number"
                  step={0.001}
                />
                <SettingItem
                  label="Input Latency (s)"
                  value={settings.ui.clickDelay}
                  onChange={(v) => handleInputChange('ui', 'clickDelay', v)}
                  type="number"
                  step={0.01}
                />
             </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="pt-8 flex items-center justify-center gap-8 border-t border-white/5 opacity-30 grayscale hover:grayscale-0 transition-all">
          <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
            <Cpu className="w-3 h-3" />
            V-ENGINE 2.2.0
          </div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
            <Database className="w-3 h-3" />
            DB_LOCAL_STORAGE
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
