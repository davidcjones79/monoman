import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { Card } from './Card';
import { formatBytes, formatRate } from '../utils/format';
import type { NetworkMetrics, NetworkRates, MetricsHistory } from '../types';

interface NetworkPanelProps {
  network: NetworkMetrics;
  rates: Record<string, NetworkRates>;
  history: MetricsHistory;
}

export function NetworkPanel({ network, rates, history }: NetworkPanelProps) {
  const safeHistory = history || { net_recv_rate: [], net_sent_rate: [] };

  // Build chart data from server-side history (already in bytes/s)
  const chartData = (safeHistory.net_recv_rate || []).map((recv, index) => ({
    index,
    in: recv / 1024 / 1024, // Convert to MB/s
    out: (safeHistory.net_sent_rate?.[index] || 0) / 1024 / 1024,
  }));

  // Calculate totals
  let totalIn = 0;
  let totalOut = 0;
  let totalBytesRecv = 0;
  let totalBytesSent = 0;

  Object.entries(network.interfaces).forEach(([name, iface]) => {
    if (iface.is_up) {
      totalBytesRecv += iface.bytes_recv;
      totalBytesSent += iface.bytes_sent;
      const ifaceRates = rates[name];
      if (ifaceRates) {
        totalIn += ifaceRates.bytes_recv_rate;
        totalOut += ifaceRates.bytes_sent_rate;
      }
    }
  });

  const activeInterfaces = Object.entries(network.interfaces).filter(
    ([, iface]) => iface.is_up
  );

  return (
    <Card title="Network">
      <div className="network-content">
        <div className="network-summary">
          <div className="network-rate">
            <span className="rate-arrow down">↓</span>
            <span className="rate-value">{formatRate(totalIn)}</span>
          </div>
          <div className="network-rate">
            <span className="rate-arrow up">↑</span>
            <span className="rate-value">{formatRate(totalOut)}</span>
          </div>
        </div>

        <div className="network-chart">
          <ResponsiveContainer width="100%" height={100}>
            <LineChart data={chartData}>
              <XAxis dataKey="index" hide />
              <YAxis hide />
              <Tooltip
                formatter={(value: number, name: string) => [
                  `${value.toFixed(2)} MB/s`,
                  name === 'in' ? 'Download' : 'Upload',
                ]}
                labelFormatter={() => ''}
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '4px',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="in"
                name="Download"
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="out"
                name="Upload"
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="network-totals">
          <div className="info-row">
            <span>Total Downloaded</span>
            <span>{formatBytes(totalBytesRecv)}</span>
          </div>
          <div className="info-row">
            <span>Total Uploaded</span>
            <span>{formatBytes(totalBytesSent)}</span>
          </div>
          <div className="info-row">
            <span>Connections</span>
            <span>{network.connections_count}</span>
          </div>
        </div>

        <div className="network-interfaces">
          <div className="interfaces-label">Interfaces</div>
          {activeInterfaces.map(([name, iface]) => {
            const ifaceRates = rates[name];
            return (
              <div key={name} className="interface-item">
                <div className="interface-name">
                  <span className="status-dot active" />
                  {name}
                  {iface.speed > 0 && (
                    <span className="interface-speed">{iface.speed} Mbps</span>
                  )}
                </div>
                <div className="interface-addresses">
                  {iface.addresses.slice(0, 2).join(', ')}
                </div>
                {ifaceRates && (
                  <div className="interface-rates">
                    <span>↓ {formatRate(ifaceRates.bytes_recv_rate)}</span>
                    <span>↑ {formatRate(ifaceRates.bytes_sent_rate)}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
