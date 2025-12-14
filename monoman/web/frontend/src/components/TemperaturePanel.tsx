import { useState } from 'react';
import { Card } from './Card';
import { formatTemperature, getPercentColor } from '../utils/format';
import type { TemperatureMetrics } from '../types';

interface TemperaturePanelProps {
  temperature: TemperatureMetrics;
}

export function TemperaturePanel({ temperature }: TemperaturePanelProps) {
  const [showRaw, setShowRaw] = useState(false);

  if (!temperature.available || Object.keys(temperature.sensors).length === 0) {
    return null;
  }

  const getTemperatureColor = (current: number, high: number | null, critical: number | null) => {
    if (critical && current >= critical) return '#ef4444';
    if (high && current >= high) return '#f97316';
    const percent = high ? (current / high) * 100 : (current / 100) * 100;
    return getPercentColor(percent);
  };

  const hasGrouped = temperature.grouped && temperature.grouped.length > 0;

  return (
    <Card title="Temperature">
      <div className="temp-content">
        {hasGrouped && (
          <div className="temp-view-toggle">
            <button
              className={`view-toggle-btn ${!showRaw ? 'active' : ''}`}
              onClick={() => setShowRaw(false)}
            >
              Summary
            </button>
            <button
              className={`view-toggle-btn ${showRaw ? 'active' : ''}`}
              onClick={() => setShowRaw(true)}
            >
              All Sensors
            </button>
          </div>
        )}

        {!showRaw && hasGrouped ? (
          // Grouped/summary view
          <div className="temp-grouped">
            {temperature.grouped.map((group) => (
              <div key={group.name} className="temp-group-item">
                <span className="temp-group-name">{group.name}</span>
                <span
                  className="temp-value"
                  style={{
                    color: getTemperatureColor(group.current, group.high, group.critical),
                  }}
                >
                  {formatTemperature(group.current)}
                </span>
                {group.high && (
                  <span className="temp-threshold">
                    / {formatTemperature(group.high)}
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          // Raw sensor view
          Object.entries(temperature.sensors).map(([sensorName, readings]) => (
            <div key={sensorName} className="temp-sensor">
              <div className="sensor-name">{sensorName}</div>
              <div className="sensor-readings">
                {readings.map((reading, index) => (
                  <div key={index} className="temp-reading">
                    <span className="temp-label">{reading.label || `Sensor ${index}`}</span>
                    <span
                      className="temp-value"
                      style={{
                        color: getTemperatureColor(reading.current, reading.high, reading.critical),
                      }}
                    >
                      {formatTemperature(reading.current)}
                    </span>
                    {reading.high && (
                      <span className="temp-threshold">
                        (High: {formatTemperature(reading.high)})
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
