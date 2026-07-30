import type {
  AgentType,
  ActionType,
  RiskTier,
  ImpactDirection,
} from '@/types';

/* =========================================================================
   Single source of truth for configurable values. Components read from here
   instead of hardcoding strings, numbers, colours or thresholds.
   ========================================================================= */

export const APP_CONFIG = {
  brand: {
    name: 'VyaparAI',
    tagline: 'Your AI team that runs your store.',
  },

  currency: {
    code: 'INR',
    locale: 'en-IN',
  },

  /** Confidence thresholds drive routing + labelling. */
  confidence: {
    /** at/above this, a GREEN card is eligible for full-auto (future sprint) */
    autoThreshold: 85,
    /** at/above this we label it "high confidence" and allow batch-approve */
    highThreshold: 75,
  },

  /** Default snooze duration (hours). Configurable per account later. */
  snoozeHours: 24,

  /** Keyboard shortcuts (single source so help + handlers never drift). */
  shortcuts: {
    approve: 'a',
    edit: 'e',
    snooze: 's',
    dismiss: 'x',
    toggleWhy: '?',
    command: 'k', // used with meta/ctrl
    next: 'j',
    prev: 'k',
  },
} as const;

/* ---- Risk tiers -------------------------------------------------------- */
export interface RiskTierMeta {
  label: string;
  description: string;
  /** CSS variable names, so colours stay in theme.css */
  fgVar: string;
  bgVar: string;
}

export const RISK_TIERS: Record<RiskTier, RiskTierMeta> = {
  GREEN: {
    label: 'Low risk',
    description: 'Reversible, low-stakes. Eligible for auto later.',
    fgVar: '--tier-green-fg',
    bgVar: '--tier-green-bg',
  },
  YELLOW: {
    label: 'Needs approval',
    description: 'Meaningful but reversible. Always requires your OK.',
    fgVar: '--tier-amber-fg',
    bgVar: '--tier-amber-bg',
  },
  RED: {
    label: 'High risk',
    description: 'Irreversible or customer-facing. Explicit confirmation.',
    fgVar: '--tier-red-fg',
    bgVar: '--tier-red-bg',
  },
};

/* ---- Agents ------------------------------------------------------------ */
export const AGENTS: Record<AgentType, { label: string }> = {
  INVENTORY: { label: 'Inventory' },
  PRICING: { label: 'Pricing' },
  SUPPORT: { label: 'Support' },
  RETURNS: { label: 'Returns' },
  MARKETING: { label: 'Marketing' },
  LISTING: { label: 'Listing' },
  ANALYTICS: { label: 'Analytics' },
  MANAGER: { label: 'Manager' },
};

/* ---- Action types (human labels) -------------------------------------- */
export const ACTION_TYPES: Record<ActionType, { label: string }> = {
  REORDER: { label: 'Reorder stock' },
  LOW_STOCK_ALERT: { label: 'Low stock' },
  PRICE_FIX: { label: 'Price change' },
  PROFIT_LEAK: { label: 'Profit leak' },
  REPLY_DRAFT: { label: 'Customer reply' },
  LISTING_FIX: { label: 'Listing fix' },
  MARKETING_ACTION: { label: 'Marketing' },
  RETURN_ALERT: { label: 'Returns' },
};

/* ---- Impact direction labels ------------------------------------------ */
export const IMPACT_DIRECTION: Record<
  ImpactDirection,
  { label: string; verb: string }
> = {
  SAVES: { label: 'Saves', verb: 'save' },
  EARNS: { label: 'Earns', verb: 'earn' },
  PROTECTS: { label: 'Protects', verb: 'protect' },
};

/* ---- Dashboard section copy ------------------------------------------- */
export const SECTIONS = {
  needsApproval: {
    title: 'Needs your approval',
    subtitle: 'Review and decide. Fastest path: approve high-confidence.',
    emptyText: "You're all caught up. Nothing needs you right now.",
  },
  doneForYou: {
    title: 'Done for you',
    subtitle: 'Completed automatically. Everything here can be undone.',
    emptyText: 'Nothing has run automatically yet.',
  },
  watching: {
    title: 'Watching',
    subtitle: 'Trends approaching action. No decision needed yet.',
    emptyText: 'Nothing on the watchlist.',
  },
  activity: {
    title: 'Activity',
    subtitle: 'A full record of what happened and when.',
    emptyText: 'No activity yet.',
  },
} as const;
