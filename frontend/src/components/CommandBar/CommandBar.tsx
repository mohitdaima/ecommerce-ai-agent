import { useEffect, useRef, useState } from 'react';
import { useUiStore } from '@/store/useUiStore';
import { APP_CONFIG } from '@/config/app.config';
import { Kbd } from '@/components/ui/Kbd';
import styles from './CommandBar.module.css';

interface Msg {
  role: 'user' | 'ai';
  text: string;
}

/**
 * The command bar — chat DEMOTED to a secondary, on-demand palette (opens with
 * Cmd/Ctrl+K). It is no longer the home screen. Sprint 1 keeps this as a light
 * ask box; wiring it to the backend command handler is a later sprint.
 */
export function CommandBar() {
  const open = useUiStore((s) => s.commandOpen);
  const close = useUiStore((s) => s.closeCommand);
  const [value, setValue] = useState('');
  const [log, setLog] = useState<Msg[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) inputRef.current?.focus();
    else {
      setValue('');
      setLog([]);
    }
  }, [open]);

  if (!open) return null;

  function submit() {
    const q = value.trim();
    if (!q) return;
    // Sprint 1 stub: acknowledge locally. Real routing to agents comes later.
    setLog((l) => [
      ...l,
      { role: 'user', text: q },
      {
        role: 'ai',
        text: 'Got it — command routing to the agents is coming in a later sprint. For now, actions live in your Approval Inbox.',
      },
    ]);
    setValue('');
  }

  return (
    <div
      className={styles.overlay}
      onClick={close}
      role="dialog"
      aria-modal="true"
    >
      <div className={styles.panel} onClick={(e) => e.stopPropagation()}>
        <div className={styles.inputRow}>
          <span className={styles.prompt}>›</span>
          <input
            ref={inputRef}
            className={styles.input}
            placeholder="Ask VyaparAI or type a command…"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') submit();
              if (e.key === 'Escape') close();
            }}
          />
        </div>
        {log.length > 0 && (
          <div className={styles.log}>
            {log.map((m, i) => (
              <div
                key={i}
                className={`${styles.msg} ${
                  m.role === 'user' ? styles.msgUser : styles.msgAI
                }`}
              >
                {m.role === 'user' ? 'You: ' : ''}
                {m.text}
              </div>
            ))}
          </div>
        )}
        <div className={styles.hint}>
          <Kbd>{APP_CONFIG.shortcuts.command.toUpperCase()}</Kbd> with{' '}
          {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'} to toggle ·{' '}
          <Kbd>Esc</Kbd> to close
        </div>
      </div>
    </div>
  );
}
