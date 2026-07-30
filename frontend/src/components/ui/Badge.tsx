import type { CSSProperties, ReactNode } from 'react';
import styles from './ui.module.css';

interface BadgeProps {
  children: ReactNode;
  /** CSS variable names from theme.css, keeping colours out of components. */
  fgVar?: string;
  bgVar?: string;
  title?: string;
}

export function Badge({ children, fgVar, bgVar, title }: BadgeProps) {
  const style: CSSProperties = {
    color: fgVar ? `var(${fgVar})` : 'var(--color-text-muted)',
    background: bgVar ? `var(${bgVar})` : 'var(--color-surface-2)',
  };
  return (
    <span className={styles.badge} style={style} title={title}>
      {children}
    </span>
  );
}
