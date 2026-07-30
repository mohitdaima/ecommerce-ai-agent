import { useMemo } from 'react';
import { useActionStore } from '@/store/useActionStore';
import { selectWatching } from '@/lib/actionCard.logic';
import { SECTIONS } from '@/config/app.config';
import { Section } from '@/components/ui/Section';
import styles from './dashboard.module.css';

/** Bottom zone: sub-threshold trends. Compact, informational, no actions. */
export function Watching() {
  const cards = useActionStore((s) => s.cards);
  const items = useMemo(() => selectWatching(cards), [cards]);

  return (
    <Section
      title={SECTIONS.watching.title}
      subtitle={SECTIONS.watching.subtitle}
      count={items.length}
      isEmpty={items.length === 0}
      emptyText={SECTIONS.watching.emptyText}
    >
      {items.map((card) => (
        <div key={card.id} className={styles.watchRow}>
          <div style={{ flex: 1 }}>
            <div className={styles.watchTitle}>{card.title}</div>
            <div className={styles.watchMeta}>{card.why.summary}</div>
          </div>
        </div>
      ))}
    </Section>
  );
}
