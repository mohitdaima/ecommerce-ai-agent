import { useMemo } from 'react';
import { useActionStore } from '@/store/useActionStore';
import { selectDoneForYou } from '@/lib/actionCard.logic';
import { SECTIONS } from '@/config/app.config';
import { Section } from '@/components/ui/Section';
import { ActionCard } from '@/components/ActionCard/ActionCard';

/** Bottom zone: work completed automatically (read-only; Undo arrives later). */
export function DoneForYou() {
  const cards = useActionStore((s) => s.cards);
  const done = useMemo(() => selectDoneForYou(cards), [cards]);

  return (
    <Section
      title={SECTIONS.doneForYou.title}
      subtitle={SECTIONS.doneForYou.subtitle}
      count={done.length}
      isEmpty={done.length === 0}
      emptyText={SECTIONS.doneForYou.emptyText}
    >
      {done.map((card) => (
        <ActionCard key={card.id} card={card} readOnly />
      ))}
    </Section>
  );
}
