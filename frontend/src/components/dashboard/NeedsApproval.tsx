import { useMemo } from 'react';
import { useActionStore } from '@/store/useActionStore';
import { useUiStore } from '@/store/useUiStore';
import { useActions } from '@/hooks/useActions';
import {
  selectNeedsApproval,
  selectBatchApprovable,
} from '@/lib/actionCard.logic';
import { SECTIONS } from '@/config/app.config';
import { Section } from '@/components/ui/Section';
import { ActionCard } from '@/components/ActionCard/ActionCard';
import styles from './dashboard.module.css';

/** Middle zone: the approval queue, impact-ordered. The heart of the product. */
export function NeedsApproval() {
  const cards = useActionStore((s) => s.cards);
  const selectedId = useUiStore((s) => s.selectedCardId);
  const select = useUiStore((s) => s.select);
  const { approve, edit, snooze, dismiss, approveMany } = useActions();

  const queue = useMemo(() => selectNeedsApproval(cards), [cards]);
  const batch = useMemo(() => selectBatchApprovable(cards), [cards]);

  const batchAction =
    batch.length > 0 ? (
      <button className={styles.batchBtn} onClick={() => approveMany(batch)}>
        Approve all high-confidence ({batch.length})
      </button>
    ) : undefined;

  return (
    <Section
      title={SECTIONS.needsApproval.title}
      subtitle={SECTIONS.needsApproval.subtitle}
      count={queue.length}
      action={batchAction}
      isEmpty={queue.length === 0}
      emptyText={SECTIONS.needsApproval.emptyText}
    >
      {queue.map((card) => (
        <ActionCard
          key={card.id}
          card={card}
          selected={card.id === selectedId}
          onSelect={select}
          onApprove={approve}
          onEdit={edit}
          onSnooze={snooze}
          onDismiss={dismiss}
        />
      ))}
    </Section>
  );
}
