import { create } from 'zustand';
import type { ActionCard, CardAction, ActivityEntry } from '@/types';
import { actionCardService } from '@/services/actionCardService';
import { applyAction } from '@/lib/actionCard.logic';
import { useActivityStore } from './useActivityStore';

/* =========================================================================
   The Action Card store. It owns the card list and is the ONLY place a card
   changes state. Every decision routes through `dispatch`, which:
     1) applies the pure transition (lib),
     2) records an append-only activity entry (ledger),
     3) (future) calls service.execute() for GREEN/approved cards.
   This single choke-point is what lets Execution/Undo/Autopilot slot in
   later without touching the UI.
   ========================================================================= */

interface ActionState {
  cards: ActionCard[];
  loading: boolean;
  load: () => Promise<void>;
  dispatch: (
    id: string,
    action: CardAction,
    patch?: Partial<Pick<ActionCard, 'recommendation'>>,
  ) => void;
  batchApprove: (ids: string[]) => void;
}

function activityFor(card: ActionCard, action: CardAction): ActivityEntry {
  const verbs: Record<CardAction, string> = {
    APPROVE: 'Approved',
    EDIT: 'Edited & approved',
    SNOOZE: 'Snoozed',
    DISMISS: 'Dismissed',
  };
  return {
    id: `act_${card.id}_${Date.now()}`,
    timestamp: new Date().toISOString(),
    actor: 'SELLER',
    agent: card.agent,
    cardId: card.id,
    actionTaken: `${verbs[action]}: ${card.title}`,
    confidence: card.confidence,
    outcome: action === 'SNOOZE' ? 'PENDING' : 'SUCCESS',
  };
}

export const useActionStore = create<ActionState>((set, get) => ({
  cards: [],
  loading: true,

  load: async () => {
    set({ loading: true });
    const cards = await actionCardService.fetchCards();
    set({ cards, loading: false });
  },

  dispatch: (id, action, patch) => {
    const card = get().cards.find((c) => c.id === id);
    if (!card) return;
    const next = applyAction(card, action, patch);
    set((state) => ({
      cards: state.cards.map((c) => (c.id === id ? next : c)),
    }));
    useActivityStore.getState().record(activityFor(next, action));
  },

  batchApprove: (ids) => {
    ids.forEach((id) => get().dispatch(id, 'APPROVE'));
  },
}));
