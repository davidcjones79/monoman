import { useState, useEffect, useCallback } from 'react';
import { useMetrics } from './hooks/useMetrics';
import { useTheme } from './hooks/useTheme';
import { SystemPanel } from './components/SystemPanel';
import { CPUPanel } from './components/CPUPanel';
import { MemoryPanel } from './components/MemoryPanel';
import { NetworkPanel } from './components/NetworkPanel';
import { DiskPanel } from './components/DiskPanel';
import { ProcessPanel } from './components/ProcessPanel';
import { GPUPanel } from './components/GPUPanel';
import { TemperaturePanel } from './components/TemperaturePanel';
import { ConfigPanel } from './components/ConfigPanel';
import { HistoryPage } from './components/HistoryPage';
import './App.css';

type View = 'dashboard' | 'history';

function App() {
  const { metrics, history, config, connected, error, updateConfig, clearHistory } =
    useMetrics();
  const { theme, toggleTheme } = useTheme();
  const [showConfig, setShowConfig] = useState(false);
  const [currentView, setCurrentView] = useState<View>('dashboard');

  // Keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Ignore if typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case '?':
          setShowConfig((prev) => !prev);
          break;
        case 'Escape':
          setShowConfig(false);
          break;
        case 'h':
        case 'H':
          setCurrentView((prev) => (prev === 'dashboard' ? 'history' : 'dashboard'));
          break;
        case 't':
        case 'T':
          toggleTheme();
          break;
        case '+':
        case '=':
          if (config) {
            updateConfig({ refresh_interval: Math.min(10, config.refresh_interval + 0.5) });
          }
          break;
        case '-':
          if (config) {
            updateConfig({ refresh_interval: Math.max(0.5, config.refresh_interval - 0.5) });
          }
          break;
        case '1':
          if (config) {
            updateConfig({ panels: { ...config.panels, dashboard: !config.panels.dashboard } });
          }
          break;
        case '2':
          if (config) {
            updateConfig({ panels: { ...config.panels, cpu: !config.panels.cpu } });
          }
          break;
        case '3':
          if (config) {
            updateConfig({ panels: { ...config.panels, memory: !config.panels.memory } });
          }
          break;
        case '4':
          if (config) {
            updateConfig({ panels: { ...config.panels, disk: !config.panels.disk } });
          }
          break;
        case '5':
          if (config) {
            updateConfig({ panels: { ...config.panels, network: !config.panels.network } });
          }
          break;
        case '6':
          if (config) {
            updateConfig({ panels: { ...config.panels, processes: !config.panels.processes } });
          }
          break;
        case '7':
          if (config) {
            updateConfig({ panels: { ...config.panels, gpu: !config.panels.gpu } });
          }
          break;
        case '8':
          if (config) {
            updateConfig({
              panels: { ...config.panels, temperature: !config.panels.temperature },
            });
          }
          break;
      }
    },
    [config, updateConfig, toggleTheme]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (error) {
    return (
      <div className="app">
        <div className="error-container">
          <h1>Connection Error</h1>
          <p>{error}</p>
          <p>Make sure the Monoman API server is running on port 8000.</p>
          <code>monoman-web</code>
        </div>
      </div>
    );
  }

  if (!metrics && currentView === 'dashboard') {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Connecting to Monoman...</p>
        </div>
      </div>
    );
  }

  // Show history page
  if (currentView === 'history') {
    return (
      <div className="app">
        <HistoryPage onBack={() => setCurrentView('dashboard')} />
      </div>
    );
  }

  // At this point we know we're on dashboard and metrics must be defined
  if (!metrics) {
    return null;
  }

  const panels = config?.panels || {
    dashboard: true,
    cpu: true,
    memory: true,
    disk: true,
    network: true,
    processes: true,
    gpu: true,
    temperature: true,
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Monoman</h1>
        <div className="header-status">
          <button
            className="nav-button"
            onClick={() => setCurrentView('history')}
            title="Historical Graphs (H)"
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z" />
            </svg>
            History
          </button>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme (T)`}
          >
            {theme === 'dark' ? (
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z" />
              </svg>
            )}
          </button>
          <button className="settings-button" onClick={() => setShowConfig(true)} title="Settings (?)">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" />
            </svg>
          </button>
          <span className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
            {connected ? 'Connected' : 'Reconnecting...'}
          </span>
          {config && (
            <span className="refresh-rate" title="Refresh interval">
              {config.refresh_interval}s
            </span>
          )}
          <span className="last-update">{new Date(metrics.timestamp).toLocaleTimeString()}</span>
        </div>
      </header>

      <main className="dashboard">
        <div className="dashboard-grid">
          {panels.dashboard && <SystemPanel system={metrics.system_info} />}
          {panels.cpu && <CPUPanel cpu={metrics.cpu} history={history} />}
          {panels.memory && <MemoryPanel memory={metrics.memory} history={history} />}
          {panels.network && (
            <NetworkPanel network={metrics.network} rates={metrics.network_rates} history={history} />
          )}
          {panels.disk && (
            <DiskPanel disk={metrics.disk} rates={metrics.disk_rates} history={history} />
          )}
          {panels.gpu && <GPUPanel gpu={metrics.gpu} />}
          {panels.temperature && <TemperaturePanel temperature={metrics.temperature} />}
          {panels.processes && <ProcessPanel processes={metrics.processes} />}
        </div>
      </main>

      {showConfig && config && (
        <ConfigPanel
          config={config}
          onUpdateConfig={updateConfig}
          onClearHistory={clearHistory}
          onClose={() => setShowConfig(false)}
        />
      )}
    </div>
  );
}

export default App;
