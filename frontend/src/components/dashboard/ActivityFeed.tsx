import { useActivityStore } from '@/store/useActivityStore';
import { SECTIONS, AGENTS } from '@/config/app.config';
import { formatRelativeTime } from '@/lib/format';
import { Section } from '@/components/ui/Section';
import styles from './dashboard.module.css';

/** Bottom zone: append-only record of everything that happened. */
export function ActivityFeed() {
  const entries = useActivityStore((s) => s.entries);

  return (
    <Section
      title={SECTIONS.activity.title}
      subtitle={SECTIONS.activity.subtitle}
      count={entries.length}
      isEmpty={entries.length === 0}
      emptyText={SECTIONS.activity.emptyText}
    >
      <div className={styles.feed}>
        {entries.map((e) => (
          <div key={e.id} className={styles.feedItem}>
            <span className={styles.feedDot} />
            <span className={styles.feedText}>
              {e.actionTaken}{' '}
              <span className={styles.feedActor}>
                — {e.actor === 'AGENT' && e.agent ? AGENTS[e.agent].label : e.actor.toLowerCase()}
              </span>
            </span>
            <span className={styles.feedTime}>
              {formatRelativeTime(e.timestamp)}
            </span>
          </div>
        ))}
      </div>
    </Section>
  );
}
