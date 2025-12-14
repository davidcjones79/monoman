// Monoman API types - mirrors Python dataclasses

export interface SystemInfo {
  hostname: string;
  platform: string;
  platform_release: string;
  platform_version: string;
  architecture: string;
  processor: string;
  python_version: string;
  boot_time: string | null;
  uptime_seconds: number;
}

export interface CPUMetrics {
  percent_total: number;
  percent_per_core: number[];
  load_avg_1: number;
  load_avg_5: number;
  load_avg_15: number;
  frequency_current: number;
  frequency_max: number;
  core_count: number;
  thread_count: number;
  ctx_switches: number;
  interrupts: number;
  user_time: number;
  system_time: number;
  idle_time: number;
  iowait_time: number;
}

export interface MemoryMetrics {
  total: number;
  available: number;
  used: number;
  free: number;
  percent: number;
  cached: number;
  buffers: number;
  swap_total: number;
  swap_used: number;
  swap_free: number;
  swap_percent: number;
}

export interface DiskPartitionMetrics {
  device: string;
  mountpoint: string;
  fstype: string;
  total: number;
  used: number;
  free: number;
  percent: number;
}

export interface DiskIOMetrics {
  device: string;
  read_bytes: number;
  write_bytes: number;
  read_count: number;
  write_count: number;
  read_time: number;
  write_time: number;
  busy_time: number;
}

export interface DiskMetrics {
  partitions: DiskPartitionMetrics[];
  io: Record<string, DiskIOMetrics>;
}

export interface NetworkInterfaceMetrics {
  name: string;
  bytes_sent: number;
  bytes_recv: number;
  packets_sent: number;
  packets_recv: number;
  errors_in: number;
  errors_out: number;
  drops_in: number;
  drops_out: number;
  is_up: boolean;
  speed: number;
  addresses: string[];
}

export interface NetworkMetrics {
  interfaces: Record<string, NetworkInterfaceMetrics>;
  connections_count: number;
}

export interface ProcessMetrics {
  pid: number;
  name: string;
  username: string;
  status: string;
  cpu_percent: number;
  memory_percent: number;
  memory_rss: number;
  memory_vms: number;
  threads: number;
  create_time: number;
  cmdline: string;
  nice: number;
  io_read_bytes: number;
  io_write_bytes: number;
}

export interface ProcessListMetrics {
  processes: ProcessMetrics[];
  total_count: number;
  running_count: number;
  sleeping_count: number;
  stopped_count: number;
}

export interface GPUMetrics {
  index: number;
  name: string;
  driver_version: string;
  memory_total: number;
  memory_used: number;
  memory_free: number;
  memory_percent: number;
  utilization: number;
  temperature: number;
  fan_speed: number;
  power_draw: number;
  power_limit: number;
}

export interface GPUListMetrics {
  gpus: GPUMetrics[];
  available: boolean;
}

export interface TemperatureReading {
  label: string;
  current: number;
  high: number | null;
  critical: number | null;
}

export interface GroupedTemperature {
  name: string;
  current: number;
  high: number | null;
  critical: number | null;
  source_labels: string[];
}

export interface TemperatureMetrics {
  sensors: Record<string, TemperatureReading[]>;
  grouped: GroupedTemperature[];
  available: boolean;
}

export interface NetworkRates {
  bytes_sent_rate: number;
  bytes_recv_rate: number;
  packets_sent_rate: number;
  packets_recv_rate: number;
}

export interface DiskRates {
  read_bytes_rate: number;
  write_bytes_rate: number;
  read_count_rate: number;
  write_count_rate: number;
}

export interface MetricsHistory {
  cpu_total: number[];
  cpu_user: number[];
  cpu_system: number[];
  memory_percent: number[];
  swap_percent: number[];
  net_recv_rate: number[];
  net_sent_rate: number[];
  disk_read_rate: number[];
  disk_write_rate: number[];
  gpu_util: number[];
  gpu_memory: number[];
  gpu_temp: number[];
  [key: string]: number[]; // For per-core CPU (cpu_core_0, cpu_core_1, etc.)
}

export interface Snapshot {
  timestamp: string;
  system_info: SystemInfo;
  cpu: CPUMetrics;
  memory: MemoryMetrics;
  disk: DiskMetrics;
  network: NetworkMetrics;
  processes: ProcessListMetrics;
  gpu: GPUListMetrics;
  temperature: TemperatureMetrics;
  network_rates: Record<string, NetworkRates>;
  disk_rates: Record<string, DiskRates>;
  history?: MetricsHistory;
}

export interface PanelVisibility {
  dashboard: boolean;
  cpu: boolean;
  memory: boolean;
  disk: boolean;
  network: boolean;
  processes: boolean;
  gpu: boolean;
  temperature: boolean;
}

export interface Config {
  refresh_interval: number;
  max_history_points: number;
  process_sort_by: string;
  process_sort_reverse: boolean;
  panels: PanelVisibility;
}
