import { useState, useEffect, useCallback } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { Card } from './Card';

interface HistoryPageProps {
  onBack: () => void;
}

interface MetricSeries {
  values: number[];
  timestamps: string[];
}

interface HistoricalResponse {
  cpu_total?: MetricSeries;
  cpu_user?: MetricSeries;
  cpu_system?: MetricSeries;
  memory_percent?: MetricSeries;
  swap_percent?: MetricSeries;
  net_recv_rate?: MetricSeries;
  net_sent_rate?: MetricSeries;
  disk_read_rate?: MetricSeries;
  disk_write_rate?: MetricSeries;
}

interface ChartDataPoint {
  time: string;
  timestamp: string;
  cpu_total: number;
  cpu_user: number;
  cpu_system: number;
  memory: number;
  swap: number;
  net_in: number;
  net_out: number;
  disk_read: number;
  disk_write: number;
}

type TimeRange = '5m' | '30m' | '1h' | '6h' | '24h' | '7d';

const TIME_RANGES: { value: TimeRange; label: string }[] = [
  { value: '5m', label: '5 min' },
  { value: '30m', label: '30 min' },
  { value: '1h', label: '1 hour' },
  { value: '6h', label: '6 hours' },
  { value: '24h', label: '24 hours' },
  { value: '7d', label: '7 days' },
];

export function HistoryPage({ onBack }: HistoryPageProps) {
  const [range, setRange] = useState<TimeRange>('30m');
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Format timestamp for display
  const formatTime = useCallback((timestamp: string) => {
    const date = new Date(timestamp);
    if (range === '7d' || range === '24h') {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }, [range]);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/metrics/history?range=${range}`);
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const result: HistoricalResponse = await response.json();

      // Transform the API response into chart-friendly data
      // Use cpu_total timestamps as the reference (all metrics should have same timestamps)
      const timestamps = result.cpu_total?.timestamps || [];
      const transformed: ChartDataPoint[] = timestamps.map((ts, i) => ({
        time: formatTime(ts),
        timestamp: ts,
        cpu_total: result.cpu_total?.values[i] || 0,
        cpu_user: result.cpu_user?.values[i] || 0,
        cpu_system: result.cpu_system?.values[i] || 0,
        memory: result.memory_percent?.values[i] || 0,
        swap: result.swap_percent?.values[i] || 0,
        net_in: (result.net_recv_rate?.values[i] || 0) / 1024 / 1024,
        net_out: (result.net_sent_rate?.values[i] || 0) / 1024 / 1024,
        disk_read: (result.disk_read_rate?.values[i] || 0) / 1024 / 1024,
        disk_write: (result.disk_write_rate?.values[i] || 0) / 1024 / 1024,
      }));

      setChartData(transformed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch history');
    } finally {
      setLoading(false);
    }
  }, [range, formatTime]);

  useEffect(() => {
    fetchHistory();
    // Refresh every 10 seconds
    const interval = setInterval(fetchHistory, 10000);
    return () => clearInterval(interval);
  }, [fetchHistory]);

  const tooltipStyle = {
    backgroundColor: '#1f2937',
    border: '1px solid #374151',
    borderRadius: '4px',
  };

  return (
    <div className="history-page">
      <header className="history-header">
        <button className="back-button" onClick={onBack}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
          </svg>
          Back to Dashboard
        </button>
        <h1>Historical Metrics</h1>
        <div className="range-selector">
          {TIME_RANGES.map(({ value, label }) => (
            <button
              key={value}
              className={`range-button ${range === value ? 'active' : ''}`}
              onClick={() => setRange(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </header>

      {loading && chartData.length === 0 ? (
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Loading historical data...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <h2>Error loading data</h2>
          <p>{error}</p>
          <button onClick={fetchHistory}>Retry</button>
        </div>
      ) : chartData.length === 0 ? (
        <div className="empty-state">
          <h2>No historical data available</h2>
          <p>Data will appear here as the system collects metrics over time.</p>
        </div>
      ) : (
        <div className="history-charts">
          <Card title="CPU Usage">
            <div className="history-chart">
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="histCpuGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                    </linearGradient>
                    <linearGradient id="histUserGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                    </linearGradient>
                    <linearGradient id="histSystemGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="time"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    domain={[0, 100]}
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${value.toFixed(1)}%`,
                      name === 'cpu_user' ? 'User' : name === 'cpu_system' ? 'System' : 'Total',
                    ]}
                    contentStyle={tooltipStyle}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="cpu_user"
                    name="User"
                    stackId="1"
                    stroke="#3b82f6"
                    fill="url(#histUserGradient)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="cpu_system"
                    name="System"
                    stackId="1"
                    stroke="#f97316"
                    fill="url(#histSystemGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Memory Usage">
            <div className="history-chart">
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="histMemGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1} />
                    </linearGradient>
                    <linearGradient id="histSwapGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="time"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    domain={[0, 100]}
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${value.toFixed(1)}%`,
                      name === 'memory' ? 'Memory' : 'Swap',
                    ]}
                    contentStyle={tooltipStyle}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="memory"
                    name="Memory"
                    stroke="#8b5cf6"
                    fill="url(#histMemGradient)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="swap"
                    name="Swap"
                    stroke="#f97316"
                    fill="url(#histSwapGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Network I/O">
            <div className="history-chart">
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="time"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickFormatter={(value) => `${value.toFixed(1)} MB/s`}
                  />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${value.toFixed(2)} MB/s`,
                      name === 'net_in' ? 'Download' : 'Upload',
                    ]}
                    contentStyle={tooltipStyle}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="net_in"
                    name="Download"
                    stroke="#22c55e"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="net_out"
                    name="Upload"
                    stroke="#f97316"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Disk I/O">
            <div className="history-chart">
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="time"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickFormatter={(value) => `${value.toFixed(1)} MB/s`}
                  />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${value.toFixed(2)} MB/s`,
                      name === 'disk_read' ? 'Read' : 'Write',
                    ]}
                    contentStyle={tooltipStyle}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="disk_read"
                    name="Read"
                    stroke="#22c55e"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="disk_write"
                    name="Write"
                    stroke="#f97316"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <div className="history-stats">
            <Card title="Statistics">
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Data Points</span>
                  <span className="stat-value">{chartData.length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Time Range</span>
                  <span className="stat-value">
                    {TIME_RANGES.find((r) => r.value === range)?.label}
                  </span>
                </div>
                {chartData.length > 0 && (
                  <>
                    <div className="stat-item">
                      <span className="stat-label">Avg CPU</span>
                      <span className="stat-value">
                        {(chartData.reduce((sum, d) => sum + d.cpu_total, 0) / chartData.length).toFixed(1)}%
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Avg Memory</span>
                      <span className="stat-value">
                        {(chartData.reduce((sum, d) => sum + d.memory, 0) / chartData.length).toFixed(1)}%
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Peak CPU</span>
                      <span className="stat-value">
                        {Math.max(...chartData.map((d) => d.cpu_total)).toFixed(1)}%
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Peak Memory</span>
                      <span className="stat-value">
                        {Math.max(...chartData.map((d) => d.memory)).toFixed(1)}%
                      </span>
                    </div>
                  </>
                )}
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
