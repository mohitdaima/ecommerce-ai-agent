import { useMemo } from 'react';
import { useActionStore } from '@/store/useActionStore';
import type { ActionCard } from '@/types';

/* Thin bridge so components call intent-named handlers instead of reaching
   into the store shape directly. Keeps UI decoupled from store internals. */
export function useActions() {
  const dispatch = useActionStore((s) => s.dispatch);
  const batchApprove = useActionStore((s) => s.batchApprove);

  return useMemo(
    () => ({
      approve: (id: string) => dispatch(id, 'APPROVE'),
      edit: (id: string, recommendation: string) =>
        dispatch(id, 'EDIT', { recommendation }),
      snooze: (id: string) => dispatch(id, 'SNOOZE'),
      dismiss: (id: string) => dispatch(id, 'DISMISS'),
      approveMany: (cards: ActionCard[]) => batchApprove(cards.map((c) => c.id)),
    }),
    [dispatch, batchApprove],
  );
}
