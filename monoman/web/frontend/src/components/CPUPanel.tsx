import { useState } from 'react';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { Card } from './Card';
import { ProgressBar } from './ProgressBar';
import { formatFrequency, formatPercent } from '../utils/format';
import type { CPUMetrics, MetricsHistory } from '../types';

interface CPUPanelProps {
  cpu: CPUMetrics;
  history: MetricsHistory;
}

type ChartMode = 'total' | 'breakdown' | 'cores';

const CORE_COLORS = [
  '#3b82f6', '#22c55e', '#f97316', '#8b5cf6',
  '#ec4899', '#14b8a6', '#eab308', '#ef4444',
  '#06b6d4', '#84cc16', '#f43f5e', '#6366f1',
  '#10b981', '#a855f7', '#f59e0b', '#64748b',
];

export function CPUPanel({ cpu, history }: CPUPanelProps) {
  const [chartMode, setChartMode] = useState<ChartMode>('total');

  // Ensure history exists with defaults
  const safeHistory = history || {
    cpu_total: [],
    cpu_user: [],
    cpu_system: [],
  };

  // Build chart data based on mode
  const buildChartData = () => {
    const length = safeHistory.cpu_total?.length || 0;
    if (length === 0) return [];

    return Array.from({ length }, (_, index) => {
      const point: Record<string, number> = { index };

      if (chartMode === 'total') {
        point.total = safeHistory.cpu_total?.[index] || 0;
      } else if (chartMode === 'breakdown') {
        point.user = safeHistory.cpu_user?.[index] || 0;
        point.system = safeHistory.cpu_system?.[index] || 0;
      } else if (chartMode === 'cores') {
        // Add per-core data
        cpu.percent_per_core.forEach((_, coreIndex) => {
          const coreHistory = safeHistory[`cpu_core_${coreIndex}`];
          point[`core${coreIndex}`] = coreHistory?.[index] || 0;
        });
      }

      return point;
    });
  };

  const chartData = buildChartData();

  return (
    <Card title="CPU">
      <div className="cpu-content">
        <div className="cpu-main">
          <div className="cpu-usage">
            <span className="cpu-usage-value">{formatPercent(cpu.percent_total)}</span>
            <span className="cpu-usage-label">Total Usage</span>
          </div>
          <div className="cpu-chart">
            <div className="chart-mode-tabs">
              <button
                className={`chart-tab ${chartMode === 'total' ? 'active' : ''}`}
                onClick={() => setChartMode('total')}
              >
                Total
              </button>
              <button
                className={`chart-tab ${chartMode === 'breakdown' ? 'active' : ''}`}
                onClick={() => setChartMode('breakdown')}
              >
                User/Sys
              </button>
              <button
                className={`chart-tab ${chartMode === 'cores' ? 'active' : ''}`}
                onClick={() => setChartMode('cores')}
              >
                Cores
              </button>
            </div>

            <ResponsiveContainer width="100%" height={100}>
              {chartMode === 'total' ? (
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="index" hide />
                  <YAxis domain={[0, 100]} hide />
                  <Tooltip
                    formatter={(value: number) => [`${value.toFixed(1)}%`, 'CPU']}
                    labelFormatter={() => ''}
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '4px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="total"
                    stroke="#3b82f6"
                    fill="url(#cpuGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              ) : chartMode === 'breakdown' ? (
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="userGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                    </linearGradient>
                    <linearGradient id="systemGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="index" hide />
                  <YAxis domain={[0, 100]} hide />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${value.toFixed(1)}%`,
                      name === 'user' ? 'User' : 'System',
                    ]}
                    labelFormatter={() => ''}
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '4px',
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="user"
                    name="User"
                    stackId="1"
                    stroke="#3b82f6"
                    fill="url(#userGradient)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="system"
                    name="System"
                    stackId="1"
                    stroke="#f97316"
                    fill="url(#systemGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              ) : (
                <LineChart data={chartData}>
                  <XAxis dataKey="index" hide />
                  <YAxis domain={[0, 100]} hide />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${value.toFixed(1)}%`,
                      name.replace('core', 'Core '),
                    ]}
                    labelFormatter={() => ''}
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '4px',
                    }}
                  />
                  {cpu.percent_per_core.map((_, index) => (
                    <Line
                      key={index}
                      type="monotone"
                      dataKey={`core${index}`}
                      name={`core${index}`}
                      stroke={CORE_COLORS[index % CORE_COLORS.length]}
                      strokeWidth={1.5}
                      dot={false}
                    />
                  ))}
                </LineChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>

        <div className="cpu-details">
          <div className="cpu-breakdown">
            <ProgressBar value={cpu.user_time} label="User" />
            <ProgressBar value={cpu.system_time} label="System" />
            <ProgressBar value={cpu.iowait_time} label="I/O Wait" />
          </div>

          <div className="cpu-info">
            <div className="info-row">
              <span>Cores</span>
              <span>
                {cpu.core_count} / {cpu.thread_count} threads
              </span>
            </div>
            <div className="info-row">
              <span>Frequency</span>
              <span>{formatFrequency(cpu.frequency_current)}</span>
            </div>
            {cpu.load_avg_1 > 0 && (
              <div className="info-row">
                <span>Load Avg</span>
                <span>
                  {cpu.load_avg_1.toFixed(2)} / {cpu.load_avg_5.toFixed(2)} /{' '}
                  {cpu.load_avg_15.toFixed(2)}
                </span>
              </div>
            )}
          </div>
        </div>

        {cpu.percent_per_core.length > 0 && (
          <div className="cpu-cores">
            <div className="cores-label">Per Core</div>
            <div className="cores-grid">
              {cpu.percent_per_core.map((percent, index) => (
                <div key={index} className="core-item">
                  <span
                    className="core-label"
                    style={{ color: CORE_COLORS[index % CORE_COLORS.length] }}
                  >
                    {index}
                  </span>
                  <ProgressBar value={percent} showPercent={false} height={8} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
