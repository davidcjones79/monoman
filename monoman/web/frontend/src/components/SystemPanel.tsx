import { Card } from './Card';
import { formatUptime } from '../utils/format';
import type { SystemInfo } from '../types';

interface SystemPanelProps {
  system: SystemInfo;
}

export function SystemPanel({ system }: SystemPanelProps) {
  return (
    <Card title="System">
      <div className="system-grid">
        <div className="system-item">
          <span className="system-label">Hostname</span>
          <span className="system-value">{system.hostname}</span>
        </div>
        <div className="system-item">
          <span className="system-label">Platform</span>
          <span className="system-value">
            {system.platform} {system.platform_release}
          </span>
        </div>
        <div className="system-item">
          <span className="system-label">Architecture</span>
          <span className="system-value">{system.architecture}</span>
        </div>
        <div className="system-item">
          <span className="system-label">Uptime</span>
          <span className="system-value">{formatUptime(system.uptime_seconds)}</span>
        </div>
      </div>
    </Card>
  );
}
