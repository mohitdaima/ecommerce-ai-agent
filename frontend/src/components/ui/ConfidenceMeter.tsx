import styles from './ui.module.css';

interface ConfidenceMeterProps {
  /** 0..100 */
  value: number;
  showLabel?: boolean;
}

export function ConfidenceMeter({ value, showLabel = true }: ConfidenceMeterProps) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <span
      className={styles.meter}
      title={`Confidence ${clamped}%`}
      aria-label={`Confidence ${clamped} percent`}
    >
      <span className={styles.meterTrack}>
        <span className={styles.meterFill} style={{ width: `${clamped}%` }} />
      </span>
      {showLabel && <span>{clamped}%</span>}
    </span>
  );
}
