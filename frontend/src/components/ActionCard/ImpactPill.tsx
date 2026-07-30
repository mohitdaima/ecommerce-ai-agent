import type { Impact } from '@/types';
import { formatImpact, formatMinutesSaved } from '@/lib/format';
import styles from './ActionCard.module.css';

/** Shows the money + time value of a card. Money hidden when zero-value. */
export function ImpactPill({ impact }: { impact: Impact }) {
  const hasMoney = impact.currencyValue > 0;
  return (
    <span className={styles.impact}>
      {hasMoney && <strong>{formatImpact(impact)}</strong>}
      {impact.timeSavedMin > 0 && (
        <span className={styles.impactTime}>
          {hasMoney ? ' · ' : ''}
          saves {formatMinutesSaved(impact.timeSavedMin)}
        </span>
      )}
    </span>
  );
}
