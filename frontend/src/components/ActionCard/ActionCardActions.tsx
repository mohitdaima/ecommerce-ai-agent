import { Button } from '@/components/ui/Button';
import { Kbd } from '@/components/ui/Kbd';
import { APP_CONFIG } from '@/config/app.config';
import styles from './ActionCard.module.css';

interface Props {
  onApprove: () => void;
  onEdit: () => void;
  onSnooze: () => void;
  onDismiss: () => void;
  /** show single-key hints (only for the keyboard-focused card) */
  showHints?: boolean;
}

/** The four decisions available on every card (spec §D). Reusable. */
export function ActionCardActions({
  onApprove,
  onEdit,
  onSnooze,
  onDismiss,
  showHints = false,
}: Props) {
  const sc = APP_CONFIG.shortcuts;
  return (
    <div className={styles.actions}>
      <Button variant="primary" size="sm" onClick={onApprove}>
        Approve {showHints && <Kbd>{sc.approve.toUpperCase()}</Kbd>}
      </Button>
      <Button variant="secondary" size="sm" onClick={onEdit}>
        Edit {showHints && <Kbd>{sc.edit.toUpperCase()}</Kbd>}
      </Button>
      <Button variant="ghost" size="sm" onClick={onSnooze}>
        Snooze {showHints && <Kbd>{sc.snooze.toUpperCase()}</Kbd>}
      </Button>
      <Button variant="ghost" size="sm" onClick={onDismiss}>
        Dismiss {showHints && <Kbd>{sc.dismiss.toUpperCase()}</Kbd>}
      </Button>
    </div>
  );
}
