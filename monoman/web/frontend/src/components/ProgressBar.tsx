import { getPercentColor } from '../utils/format';

interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showPercent?: boolean;
  height?: number;
}

export function ProgressBar({
  value,
  max = 100,
  label,
  showPercent = true,
  height = 20,
}: ProgressBarProps) {
  const percent = Math.min((value / max) * 100, 100);
  const color = getPercentColor(percent);

  return (
    <div className="progress-container">
      {label && <span className="progress-label">{label}</span>}
      <div className="progress-bar" style={{ height }}>
        <div
          className="progress-fill"
          style={{
            width: `${percent}%`,
            backgroundColor: color,
          }}
        />
        {showPercent && (
          <span className="progress-text">{percent.toFixed(1)}%</span>
        )}
      </div>
    </div>
  );
}
