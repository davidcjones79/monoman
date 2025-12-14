import { useState } from 'react';
import { Card } from './Card';
import { formatBytes, formatPercent } from '../utils/format';
import type { ProcessListMetrics } from '../types';

interface ProcessPanelProps {
  processes: ProcessListMetrics;
}

type SortKey = 'cpu' | 'memory' | 'pid' | 'name';

export function ProcessPanel({ processes }: ProcessPanelProps) {
  const [sortBy, setSortBy] = useState<SortKey>('cpu');
  const [sortDesc, setSortDesc] = useState(true);
  const [filter, setFilter] = useState('');

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(key);
      setSortDesc(true);
    }
  };

  const sortedProcesses = [...processes.processes]
    .filter((p) => {
      if (!filter) return true;
      const filterLower = filter.toLowerCase();
      return (
        p.name.toLowerCase().includes(filterLower) ||
        p.username.toLowerCase().includes(filterLower) ||
        p.cmdline.toLowerCase().includes(filterLower)
      );
    })
    .sort((a, b) => {
      let cmp = 0;
      switch (sortBy) {
        case 'cpu':
          cmp = a.cpu_percent - b.cpu_percent;
          break;
        case 'memory':
          cmp = a.memory_percent - b.memory_percent;
          break;
        case 'pid':
          cmp = a.pid - b.pid;
          break;
        case 'name':
          cmp = a.name.localeCompare(b.name);
          break;
      }
      return sortDesc ? -cmp : cmp;
    })
    .slice(0, 20);

  const SortHeader = ({ label, sortKey }: { label: string; sortKey: SortKey }) => (
    <th onClick={() => handleSort(sortKey)} className="sortable">
      {label}
      {sortBy === sortKey && (
        <span className="sort-indicator">{sortDesc ? ' ▼' : ' ▲'}</span>
      )}
    </th>
  );

  return (
    <Card title="Processes" className="processes-card">
      <div className="processes-content">
        <div className="processes-header">
          <div className="processes-stats">
            <span>Total: {processes.total_count}</span>
            <span>Running: {processes.running_count}</span>
            <span>Sleeping: {processes.sleeping_count}</span>
          </div>
          <input
            type="text"
            placeholder="Filter processes..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="process-filter"
          />
        </div>

        <div className="processes-table-wrapper">
          <table className="processes-table">
            <thead>
              <tr>
                <SortHeader label="PID" sortKey="pid" />
                <SortHeader label="Name" sortKey="name" />
                <th>User</th>
                <SortHeader label="CPU" sortKey="cpu" />
                <SortHeader label="Memory" sortKey="memory" />
                <th>Threads</th>
              </tr>
            </thead>
            <tbody>
              {sortedProcesses.map((proc) => (
                <tr key={proc.pid}>
                  <td className="pid">{proc.pid}</td>
                  <td className="name" title={proc.cmdline || proc.name}>
                    {proc.name}
                  </td>
                  <td className="user">{proc.username}</td>
                  <td className="cpu">{formatPercent(proc.cpu_percent)}</td>
                  <td className="memory">
                    {formatPercent(proc.memory_percent)}
                    <span className="memory-size">({formatBytes(proc.memory_rss)})</span>
                  </td>
                  <td className="threads">{proc.threads}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  );
}
