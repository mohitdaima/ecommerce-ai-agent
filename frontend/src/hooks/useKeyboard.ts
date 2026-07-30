import { useEffect } from 'react';
import { APP_CONFIG } from '@/config/app.config';
import { useUiStore } from '@/store/useUiStore';
import { useActionStore } from '@/store/useActionStore';
import { selectNeedsApproval } from '@/lib/actionCard.logic';
import { useActions } from './useActions';

/* Global keyboard shortcuts. Operates on the currently focused card in the
   approval queue. Mirrors APP_CONFIG.shortcuts so help + handlers never drift. */
export function useKeyboard() {
  const { approve, snooze, dismiss } = useActions();

  useEffect(() => {
    const sc = APP_CONFIG.shortcuts;

    function onKey(e: KeyboardEvent) {
      const ui = useUiStore.getState();

      // Cmd/Ctrl+K toggles the command bar from anywhere.
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === sc.command) {
        e.preventDefault();
        ui.toggleCommand();
        return;
      }
      if (ui.commandOpen) return; // let the command bar own keys while open

      // Ignore typing in inputs/textareas.
      const el = e.target as HTMLElement | null;
      if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA')) return;

      const queue = selectNeedsApproval(useActionStore.getState().cards);
      if (queue.length === 0) return;

      const currentIdx = queue.findIndex((c) => c.id === ui.selectedCardId);
      const idx = currentIdx === -1 ? 0 : currentIdx;
      const selectedId = queue[idx]?.id ?? null;

      switch (e.key.toLowerCase()) {
        case sc.next: // j
          ui.select(queue[Math.min(idx + 1, queue.length - 1)]!.id);
          break;
        case sc.prev: // k
          ui.select(queue[Math.max(idx - 1, 0)]!.id);
          break;
        case sc.approve:
          if (selectedId) approve(selectedId);
          break;
        case sc.snooze:
          if (selectedId) snooze(selectedId);
          break;
        case sc.dismiss:
          if (selectedId) dismiss(selectedId);
          break;
        default:
          break;
      }
    }

    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [approve, snooze, dismiss]);
}
