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
import { ProgressBar } from './ProgressBar';
import { formatBytes, formatRate } from '../utils/format';
import type { DiskMetrics, DiskRates, MetricsHistory } from '../types';

interface DiskPanelProps {
  disk: DiskMetrics;
  rates: Record<string, DiskRates>;
  history: MetricsHistory;
}

export function DiskPanel({ disk, rates, history }: DiskPanelProps) {
  const safeHistory = history || { disk_read_rate: [], disk_write_rate: [] };

  // Calculate total I/O rates
  let totalRead = 0;
  let totalWrite = 0;

  Object.values(rates || {}).forEach((rate) => {
    totalRead += rate.read_bytes_rate;
    totalWrite += rate.write_bytes_rate;
  });

  // Build chart data
  const chartData = (safeHistory.disk_read_rate || []).map((read, index) => ({
    index,
    read: read / 1024 / 1024, // Convert to MB/s
    write: (safeHistory.disk_write_rate?.[index] || 0) / 1024 / 1024,
  }));

  return (
    <Card title="Disk">
      <div className="disk-content">
        <div className="disk-io">
          <div className="io-rate">
            <span className="io-label">Read</span>
            <span className="io-value read">{formatRate(totalRead)}</span>
          </div>
          <div className="io-rate">
            <span className="io-label">Write</span>
            <span className="io-value write">{formatRate(totalWrite)}</span>
          </div>
        </div>

        {chartData.length > 0 && (
          <div className="disk-chart">
            <ResponsiveContainer width="100%" height={80}>
              <LineChart data={chartData}>
                <XAxis dataKey="index" hide />
                <YAxis hide />
                <Tooltip
                  formatter={(value: number, name: string) => [
                    `${value.toFixed(2)} MB/s`,
                    name === 'read' ? 'Read' : 'Write',
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
                  dataKey="read"
                  name="Read"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="write"
                  name="Write"
                  stroke="#f97316"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="disk-partitions">
          {disk.partitions.map((partition) => (
            <div key={partition.mountpoint} className="partition-item">
              <div className="partition-header">
                <span className="partition-mount">{partition.mountpoint}</span>
                <span className="partition-device">{partition.device}</span>
              </div>
              <ProgressBar value={partition.percent} />
              <div className="partition-details">
                <span>
                  {formatBytes(partition.used)} / {formatBytes(partition.total)}
                </span>
                <span className="partition-free">{formatBytes(partition.free)} free</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
