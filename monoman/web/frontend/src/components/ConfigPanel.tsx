import { useState } from 'react';
import { Card } from './Card';
import type { Config, PanelVisibility } from '../types';

interface ConfigPanelProps {
  config: Config;
  onUpdateConfig: (config: Partial<Config>) => void;
  onClearHistory: () => void;
  onClose: () => void;
}

export function ConfigPanel({ config, onUpdateConfig, onClearHistory, onClose }: ConfigPanelProps) {
  const [localConfig, setLocalConfig] = useState(config);

  // Ensure panels object exists with defaults
  const panels = localConfig.panels || {
    dashboard: true,
    cpu: true,
    memory: true,
    disk: true,
    network: true,
    processes: true,
    gpu: true,
    temperature: true,
  };

  const handleRefreshChange = (value: number) => {
    const newConfig = { ...localConfig, refresh_interval: value };
    setLocalConfig(newConfig);
    onUpdateConfig({ refresh_interval: value });
  };

  const handlePanelToggle = (panel: keyof PanelVisibility) => {
    const newPanels = { ...panels, [panel]: !panels[panel] };
    const newConfig = { ...localConfig, panels: newPanels };
    setLocalConfig(newConfig);
    onUpdateConfig({ panels: newPanels });
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all historical data?')) {
      onClearHistory();
    }
  };

  return (
    <div className="config-overlay" onClick={onClose}>
      <div className="config-modal" onClick={(e) => e.stopPropagation()}>
        <Card title="Settings">
          <div className="config-content">
            <button className="config-close" onClick={onClose}>
              &times;
            </button>

            <section className="config-section">
              <h3>Refresh Interval</h3>
              <div className="config-row">
                <input
                  type="range"
                  min="0.5"
                  max="10"
                  step="0.5"
                  value={localConfig.refresh_interval}
                  onChange={(e) => handleRefreshChange(parseFloat(e.target.value))}
                  className="config-slider"
                />
                <span className="config-value">{localConfig.refresh_interval}s</span>
              </div>
            </section>

            <section className="config-section">
              <h3>Visible Panels</h3>
              <div className="config-toggles">
                {(Object.keys(panels) as Array<keyof PanelVisibility>).map((panel) => (
                  <label key={panel} className="config-toggle">
                    <input
                      type="checkbox"
                      checked={panels[panel]}
                      onChange={() => handlePanelToggle(panel)}
                    />
                    <span className="toggle-label">{panel.charAt(0).toUpperCase() + panel.slice(1)}</span>
                  </label>
                ))}
              </div>
            </section>

            <section className="config-section">
              <h3>Data Management</h3>
              <div className="config-actions">
                <button className="config-button danger" onClick={handleClearHistory}>
                  Clear History
                </button>
                <p className="config-hint">
                  Historical data is saved to ~/.monoman/web_history.json
                </p>
              </div>
            </section>

            <section className="config-section">
              <h3>Keyboard Shortcuts</h3>
              <div className="shortcuts-list">
                <div className="shortcut-item">
                  <kbd>?</kbd>
                  <span>Toggle settings</span>
                </div>
                <div className="shortcut-item">
                  <kbd>1</kbd>-<kbd>8</kbd>
                  <span>Toggle panels</span>
                </div>
                <div className="shortcut-item">
                  <kbd>+</kbd>/<kbd>-</kbd>
                  <span>Adjust refresh rate</span>
                </div>
              </div>
            </section>
          </div>
        </Card>
      </div>
    </div>
  );
}
