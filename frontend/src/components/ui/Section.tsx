import type { ReactNode } from 'react';
import styles from './ui.module.css';

interface SectionProps {
  title: string;
  subtitle?: string;
  count?: number;
  /** shown at the right of the header (e.g. a batch-approve button) */
  action?: ReactNode;
  /** shown when there are no children */
  emptyText?: string;
  isEmpty?: boolean;
  children?: ReactNode;
}

/** Generic titled section used by every dashboard zone (no duplication). */
export function Section({
  title,
  subtitle,
  count,
  action,
  emptyText,
  isEmpty,
  children,
}: SectionProps) {
  return (
    <section className={styles.section}>
      <header className={styles.sectionHead}>
        <div>
          <div className={styles.sectionTitleWrap}>
            <h2 className={styles.sectionTitle}>{title}</h2>
            {typeof count === 'number' && (
              <span className={styles.sectionCount}>{count}</span>
            )}
          </div>
          {subtitle && <p className={styles.sectionSub}>{subtitle}</p>}
        </div>
        {action}
      </header>
      {isEmpty ? (
        <div className={styles.sectionEmpty}>{emptyText}</div>
      ) : (
        children
      )}
    </section>
  );
}
