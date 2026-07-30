import type { AgentType } from './actionCard';

/* Append-only activity ledger entry (spec §B.4). In Sprint 1 it powers the
   Activity Feed; later it also backs Undo (via snapshotRef) and audit. */

export type ActivityActor = 'AGENT' | 'SELLER' | 'SYSTEM';
export type ActivityOutcome = 'PENDING' | 'SUCCESS' | 'FAILED' | 'REVERTED';

export interface ActivityEntry {
  id: string;
  timestamp: string;
  actor: ActivityActor;
  agent?: AgentType;
  cardId?: string;
  actionTaken: string;
  confidence?: number;
  outcome: ActivityOutcome;
  /** reserved for Undo in a later sprint */
  snapshotRef?: string;
}
