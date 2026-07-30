import { useMemo } from 'react';
import { useActionStore } from '@/store/useActionStore';
import {
  selectNeedsApproval,
  selectDoneForYou,
} from '@/lib/actionCard.logic';
import { formatCurrency, formatMinutesSaved } from '@/lib/format';
import styles from './dashboard.module.css';

function greeting(now = new Date()): string {
  const h = now.getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

/** Top zone: what the AI did overnight + what needs the seller now. */
export function MorningSummary() {
  const cards = useActionStore((s) => s.cards);

  const stats = useMemo(() => {
    const needs = selectNeedsApproval(cards);
    const done = selectDoneForYou(cards);
    const pendingImpact = needs.reduce(
      (sum, c) => sum + c.impact.currencyValue,
      0,
    );
    const timeSaved = done.reduce((sum, c) => sum + c.impact.timeSavedMin, 0);
    return {
      completed: done.length,
      needs: needs.length,
      pendingImpact,
      timeSaved,
    };
  }, [cards]);

  return (
    <div className={styles.summary}>
      <div className={styles.summaryGreeting}>{greeting()}.</div>
      <p className={styles.summaryLine}>
        Overnight I completed <strong>{stats.completed}</strong> tasks.{' '}
        <strong>{stats.needs}</strong> item{stats.needs === 1 ? '' : 's'} need
        your approval.
      </p>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <div className={styles.statValue}>{stats.completed}</div>
          <div className={styles.statLabel}>Done for you</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{stats.needs}</div>
          <div className={styles.statLabel}>Needs approval</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>
            {formatCurrency(stats.pendingImpact)}
          </div>
          <div className={styles.statLabel}>Impact awaiting you</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>
            {formatMinutesSaved(stats.timeSaved)}
          </div>
          <div className={styles.statLabel}>Time saved</div>
        </div>
      </div>
    </div>
  );
}
