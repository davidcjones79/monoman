import { Card } from './Card';
import { ProgressBar } from './ProgressBar';
import { formatBytes, formatTemperature } from '../utils/format';
import type { GPUListMetrics } from '../types';

interface GPUPanelProps {
  gpu: GPUListMetrics;
}

export function GPUPanel({ gpu }: GPUPanelProps) {
  if (!gpu.available || gpu.gpus.length === 0) {
    return null;
  }

  return (
    <Card title="GPU">
      <div className="gpu-content">
        {gpu.gpus.map((g) => (
          <div key={g.index} className="gpu-item">
            <div className="gpu-header">
              <span className="gpu-name">{g.name}</span>
              <span className="gpu-driver">Driver: {g.driver_version}</span>
            </div>

            <div className="gpu-metrics">
              <div className="gpu-metric">
                <span className="metric-label">Utilization</span>
                <ProgressBar value={g.utilization} />
              </div>

              <div className="gpu-metric">
                <span className="metric-label">Memory</span>
                <ProgressBar value={g.memory_percent} />
                <div className="metric-detail">
                  {formatBytes(g.memory_used)} / {formatBytes(g.memory_total)}
                </div>
              </div>

              <div className="gpu-stats">
                <div className="info-row">
                  <span>Temperature</span>
                  <span>{formatTemperature(g.temperature)}</span>
                </div>
                {g.fan_speed > 0 && (
                  <div className="info-row">
                    <span>Fan Speed</span>
                    <span>{g.fan_speed.toFixed(0)}%</span>
                  </div>
                )}
                {g.power_draw > 0 && (
                  <div className="info-row">
                    <span>Power</span>
                    <span>
                      {g.power_draw.toFixed(0)}W / {g.power_limit.toFixed(0)}W
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
