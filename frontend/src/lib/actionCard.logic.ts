import { APP_CONFIG } from '@/config/app.config';
import type { ActionCard, ActionStatus, CardAction } from '@/types';

/* =========================================================================
   Pure business logic for Action Cards. Framework-agnostic and fully
   testable: no React, no store, no side effects. The store calls into these.
   ========================================================================= */

/** Sort by monetary impact (highest first) so the queue is impact-ordered. */
export function sortByImpact(cards: ActionCard[]): ActionCard[] {
  return [...cards].sort(
    (a, b) => b.impact.currencyValue - a.impact.currencyValue,
  );
}

/** Section selectors — the dashboard zones are just filtered views. */
export function selectNeedsApproval(cards: ActionCard[]): ActionCard[] {
  return sortByImpact(cards.filter((c) => c.status === 'PROPOSED'));
}

export function selectDoneForYou(cards: ActionCard[]): ActionCard[] {
  return cards.filter(
    (c) => c.status === 'EXECUTED' || c.status === 'APPROVED',
  );
}

export function selectWatching(cards: ActionCard[]): ActionCard[] {
  return sortByImpact(cards.filter((c) => c.status === 'WATCHING'));
}

export function isHighConfidence(card: ActionCard): boolean {
  return card.confidence >= APP_CONFIG.confidence.highThreshold;
}

/** GREEN + high enough confidence => eligible for full-auto (future sprint). */
export function isAutoEligible(card: ActionCard): boolean {
  return (
    card.riskTier === 'GREEN' &&
    card.confidence >= APP_CONFIG.confidence.autoThreshold
  );
}

/** Cards that a "approve all high-confidence" batch would clear. */
export function selectBatchApprovable(cards: ActionCard[]): ActionCard[] {
  return selectNeedsApproval(cards).filter(
    (c) => isHighConfidence(c) && c.riskTier !== 'RED',
  );
}

/** Pure state transition. Returns a NEW card; never mutates.
 *  Sprint 1 maps decisions to statuses; execution/undo hook in later. */
export function applyAction(
  card: ActionCard,
  action: CardAction,
  patch?: Partial<Pick<ActionCard, 'recommendation'>>,
): ActionCard {
  const resolvedAt = new Date().toISOString();
  const nextStatusMap: Record<CardAction, ActionStatus> = {
    APPROVE: 'APPROVED',
    EDIT: 'APPROVED', // edit implies accept-with-changes
    SNOOZE: 'SNOOZED',
    DISMISS: 'DISMISSED',
  };
  const isTerminal = action !== 'SNOOZE';
  return {
    ...card,
    ...patch,
    status: nextStatusMap[action],
    resolution: isTerminal
      ? { resolvedAt, by: 'SELLER', note: action.toLowerCase() }
      : card.resolution ?? null,
  };
}

/** When a snoozed card is due to resurface (future overnight run). */
export function snoozeUntil(now: Date = new Date()): string {
  const d = new Date(now.getTime() + APP_CONFIG.snoozeHours * 3600_000);
  return d.toISOString();
}
