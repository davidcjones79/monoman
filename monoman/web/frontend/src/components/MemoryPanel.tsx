import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { Card } from './Card';
import { ProgressBar } from './ProgressBar';
import { formatBytes } from '../utils/format';
import type { MemoryMetrics, MetricsHistory } from '../types';

interface MemoryPanelProps {
  memory: MemoryMetrics;
  history: MetricsHistory;
}

export function MemoryPanel({ memory, history }: MemoryPanelProps) {
  const safeHistory = history || { memory_percent: [], swap_percent: [] };

  const chartData = (safeHistory.memory_percent || []).map((mem, index) => ({
    index,
    memory: mem,
    swap: safeHistory.swap_percent?.[index] || 0,
  }));

  return (
    <Card title="Memory">
      <div className="memory-content">
        <div className="memory-main">
          <div className="memory-usage">
            <ProgressBar value={memory.percent} />
            <div className="memory-values">
              <span>
                {formatBytes(memory.used)} / {formatBytes(memory.total)}
              </span>
            </div>
          </div>

          <div className="memory-chart">
            <ResponsiveContainer width="100%" height={80}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1} />
                  </linearGradient>
                  <linearGradient id="swapGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="index" hide />
                <YAxis domain={[0, 100]} hide />
                <Tooltip
                  formatter={(value: number, name: string) => [
                    `${value.toFixed(1)}%`,
                    name === 'memory' ? 'Memory' : 'Swap',
                  ]}
                  labelFormatter={() => ''}
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '4px',
                  }}
                />
                {memory.swap_total > 0 && <Legend />}
                <Area
                  type="monotone"
                  dataKey="memory"
                  name="Memory"
                  stroke="#8b5cf6"
                  fill="url(#memGradient)"
                  strokeWidth={2}
                />
                {memory.swap_total > 0 && (
                  <Area
                    type="monotone"
                    dataKey="swap"
                    name="Swap"
                    stroke="#f97316"
                    fill="url(#swapGradient)"
                    strokeWidth={2}
                  />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="memory-details">
          <div className="info-row">
            <span>Available</span>
            <span>{formatBytes(memory.available)}</span>
          </div>
          <div className="info-row">
            <span>Free</span>
            <span>{formatBytes(memory.free)}</span>
          </div>
          {memory.cached > 0 && (
            <div className="info-row">
              <span>Cached</span>
              <span>{formatBytes(memory.cached)}</span>
            </div>
          )}
          {memory.buffers > 0 && (
            <div className="info-row">
              <span>Buffers</span>
              <span>{formatBytes(memory.buffers)}</span>
            </div>
          )}
        </div>

        {memory.swap_total > 0 && (
          <div className="memory-swap">
            <div className="swap-label">Swap</div>
            <ProgressBar value={memory.swap_percent} />
            <div className="memory-values">
              <span>
                {formatBytes(memory.swap_used)} / {formatBytes(memory.swap_total)}
              </span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
