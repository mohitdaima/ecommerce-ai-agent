/* =========================================================================
   The ActionCard contract — the atomic unit of the whole product.
   This interface is intentionally forward-compatible: Undo, Execution,
   History, Grouping, Autopilot, Guardrails, Confidence and Explanation are
   ALL representable here, so later sprints add behaviour WITHOUT changing
   this shape. (See docs/PHASE-0-1-SPEC.md §B.)
   ========================================================================= */

export type AgentType =
  | 'INVENTORY'
  | 'PRICING'
  | 'SUPPORT'
  | 'RETURNS'
  | 'MARKETING'
  | 'LISTING'
  | 'ANALYTICS'
  | 'MANAGER';

export type ActionType =
  | 'REORDER'
  | 'LOW_STOCK_ALERT'
  | 'PRICE_FIX'
  | 'PROFIT_LEAK'
  | 'REPLY_DRAFT'
  | 'LISTING_FIX'
  | 'MARKETING_ACTION'
  | 'RETURN_ALERT';

export type RiskTier = 'GREEN' | 'YELLOW' | 'RED';

/** Full lifecycle. Sprint 1 uses a subset; the rest are reserved so the
 *  state machine (spec §D) can be completed without a type change. */
export type ActionStatus =
  | 'PROPOSED'
  | 'APPROVED'
  | 'EDITED'
  | 'SNOOZED'
  | 'DISMISSED'
  | 'EXECUTING'
  | 'EXECUTED'
  | 'FAILED'
  | 'REVERTED'
  | 'WATCHING';

export type AutopilotOrigin = 'SUGGESTED' | 'AUTO_EXECUTED';

export type ImpactDirection = 'SAVES' | 'EARNS' | 'PROTECTS';

export interface Impact {
  /** monetary value of the action, in the account's base currency (minor unit not used) */
  currencyValue: number;
  direction: ImpactDirection;
  /** minutes of manual work this replaces */
  timeSavedMin: number;
}

/** Plain-language reasoning shown behind every card. Never optional. */
export interface Explanation {
  summary: string;
  evidence: string[];
  assumptions: string[];
  whatIfWrong: string;
}

/** Machine-executable diff. Enables future Execution + Undo (snapshots). */
export interface ChangeSet {
  target: 'PRODUCT' | 'PRICE' | 'STOCK' | 'LISTING' | 'TICKET' | 'PO';
  targetId: string;
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  executor: 'INTERNAL' | 'AMAZON' | 'FLIPKART' | 'EXPORT_CSV' | 'NONE';
}

/** How a card ended. Written on terminal transitions; enables History. */
export interface Resolution {
  resolvedAt: string;
  by: 'SELLER' | 'AGENT' | 'SYSTEM';
  note?: string;
  snapshotRef?: string;
}

export interface ActionCard {
  id: string;
  createdAt: string;
  agent: AgentType;
  type: ActionType;

  /* content shown on the card */
  title: string;
  recommendation: string;
  why: Explanation;
  confidence: number; // 0..100
  impact: Impact;
  riskTier: RiskTier;

  /* lifecycle + orchestration */
  status: ActionStatus;
  autopilotOrigin: AutopilotOrigin;

  /* forward-compatible (unused UI in Sprint 1, reserved for later) */
  proposedChange?: ChangeSet; // Execution + Undo
  expiresAt?: string; // auto-dismiss stale cards
  groupId?: string | null; // Grouping / batching
  resolution?: Resolution | null; // History
}

/** The user-driven decisions available on a card (spec §D transitions). */
export type CardAction = 'APPROVE' | 'EDIT' | 'SNOOZE' | 'DISMISS';
