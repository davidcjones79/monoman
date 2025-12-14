import { useState, useEffect, useRef, useCallback } from 'react';
import type { Snapshot, Config, MetricsHistory } from '../types';

const WS_URL = 'ws://localhost:8000/ws';
const API_URL = 'http://localhost:8000';

export function useMetrics() {
  const [metrics, setMetrics] = useState<Snapshot | null>(null);
  const [config, setConfig] = useState<Config | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // Fetch initial config
  useEffect(() => {
    fetch(`${API_URL}/api/config`)
      .then((res) => res.json())
      .then(setConfig)
      .catch((e) => console.error('Failed to fetch config:', e));
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Handle config update responses
          if (data.type === 'config_updated') {
            setConfig(data.config);
            return;
          }

          // Handle error responses
          if (data.type === 'error') {
            console.error('Server error:', data.message);
            return;
          }

          // Regular metrics update - now includes history from server
          setMetrics(data as Snapshot);
        } catch (e) {
          console.error('Failed to parse message:', e);
        }
      };

      ws.onerror = () => {
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        setConnected(false);
        wsRef.current = null;

        // Attempt reconnect after 2 seconds
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 2000);
      };

      wsRef.current = ws;
    } catch (e) {
      setError('Failed to connect to WebSocket');
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  // Update config via WebSocket
  const updateConfig = useCallback((newConfig: Partial<Config>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(`config:${JSON.stringify(newConfig)}`);
    }
  }, []);

  // Clear history via REST API
  const clearHistory = useCallback(async () => {
    try {
      await fetch(`${API_URL}/api/history/clear`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to clear history:', e);
    }
  }, []);

  // Extract history from metrics (now comes from server)
  const history: MetricsHistory = metrics?.history || {
    cpu_total: [],
    cpu_user: [],
    cpu_system: [],
    memory_percent: [],
    swap_percent: [],
    net_recv_rate: [],
    net_sent_rate: [],
    disk_read_rate: [],
    disk_write_rate: [],
    gpu_util: [],
    gpu_memory: [],
    gpu_temp: [],
  };

  return {
    metrics,
    history,
    config,
    connected,
    error,
    updateConfig,
    clearHistory,
  };
}
