import type { HTMLAttributes, ReactNode } from 'react';
import styles from './ui.module.css';

interface SurfaceProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

/** Neutral elevated container used by cards and panels. */
export function Surface({ children, className, ...rest }: SurfaceProps) {
  return (
    <div className={[styles.surface, className ?? ''].join(' ')} {...rest}>
      {children}
    </div>
  );
}
