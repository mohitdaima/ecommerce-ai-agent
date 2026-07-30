import { useState } from 'react';
import type { ActionCard as ActionCardType } from '@/types';
import { Surface } from '@/components/ui/Surface';
import { ConfidenceMeter } from '@/components/ui/ConfidenceMeter';
import { AGENTS, ACTION_TYPES } from '@/config/app.config';
import { RiskTierBadge } from './RiskTierBadge';
import { ImpactPill } from './ImpactPill';
import { ActionCardActions } from './ActionCardActions';
import styles from './ActionCard.module.css';

interface ActionCardProps {
  card: ActionCardType;
  /** decision handlers — injected so the card stays presentational */
  onApprove?: (id: string) => void;
  onEdit?: (id: string, recommendation: string) => void;
  onSnooze?: (id: string) => void;
  onDismiss?: (id: string) => void;
  /** keyboard focus + hover selection */
  selected?: boolean;
  onSelect?: (id: string) => void;
  /** hide decision buttons (e.g. Done-for-you / Watching read-only views) */
  readOnly?: boolean;
}

/**
 * The Action Card — the single presentational component for a card anywhere
 * in the app. Business logic lives in the store/lib; this only renders and
 * forwards intent. All six required elements are shown: title, recommendation,
 * why, confidence, impact, risk tier + the four actions.
 */
export function ActionCard({
  card,
  onApprove,
  onEdit,
  onSnooze,
  onDismiss,
  selected = false,
  onSelect,
  readOnly = false,
}: ActionCardProps) {
  const [showWhy, setShowWhy] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(card.recommendation);

  const className = [styles.card, selected ? styles.selected : '']
    .filter(Boolean)
    .join(' ');

  function saveEdit() {
    onEdit?.(card.id, draft.trim() || card.recommendation);
    setEditing(false);
  }

  return (
    <Surface
      className={className}
      onMouseEnter={() => onSelect?.(card.id)}
      aria-label={card.title}
    >
      <div className={styles.topRow}>
        <span className={styles.agentTag}>{AGENTS[card.agent].label}</span>
        <RiskTierBadge tier={card.riskTier} />
        <span className={styles.agentTag}>· {ACTION_TYPES[card.type].label}</span>
        <span className={styles.spacer} />
        <ConfidenceMeter value={card.confidence} />
      </div>

      <h3 className={styles.title}>{card.title}</h3>

      {editing ? (
        <div className={styles.editRow}>
          <textarea
            className={styles.editInput}
            rows={3}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            autoFocus
          />
        </div>
      ) : (
        <p className={styles.recommendation}>{card.recommendation}</p>
      )}

      <div className={styles.metaRow}>
        <ImpactPill impact={card.impact} />
        <button
          className={styles.whyToggle}
          onClick={() => setShowWhy((v) => !v)}
          aria-expanded={showWhy}
        >
          {showWhy ? 'Hide why' : 'Why?'}
        </button>
      </div>

      {showWhy && (
        <div className={styles.why}>
          <span className={styles.whyLabel}>{card.why.summary}</span>
          {card.why.evidence.length > 0 && (
            <ul className={styles.whyList}>
              {card.why.evidence.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          )}
          {card.why.assumptions.length > 0 && (
            <span>Assumes: {card.why.assumptions.join('; ')}</span>
          )}
          <span>If wrong: {card.why.whatIfWrong}</span>
        </div>
      )}

      {!readOnly &&
        (editing ? (
          <div className={styles.actions}>
            <button
              className={styles.whyToggle}
              onClick={saveEdit}
              style={{ fontWeight: 600 }}
            >
              Save &amp; approve
            </button>
            <button
              className={styles.whyToggle}
              onClick={() => setEditing(false)}
              style={{ color: 'var(--color-text-subtle)' }}
            >
              Cancel
            </button>
          </div>
        ) : (
          <ActionCardActions
            showHints={selected}
            onApprove={() => onApprove?.(card.id)}
            onEdit={() => setEditing(true)}
            onSnooze={() => onSnooze?.(card.id)}
            onDismiss={() => onDismiss?.(card.id)}
          />
        ))}
    </Surface>
  );
}
