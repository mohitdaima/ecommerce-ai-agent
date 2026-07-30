import { useEffect } from 'react';
import { APP_CONFIG } from '@/config/app.config';
import { useActionStore } from '@/store/useActionStore';
import { useActivityStore } from '@/store/useActivityStore';
import { useUiStore } from '@/store/useUiStore';
import { useKeyboard } from '@/hooks/useKeyboard';
import { Dashboard } from '@/pages/Dashboard';
import { CommandBar } from '@/components/CommandBar/CommandBar';
import { Kbd } from '@/components/ui/Kbd';
import header from '@/components/dashboard/dashboard.module.css';

export default function App() {
  const loadCards = useActionStore((s) => s.load);
  const loadActivity = useActivityStore((s) => s.load);
  const openCommand = useUiStore((s) => s.openCommand);

  useKeyboard();

  useEffect(() => {
    void loadCards();
    void loadActivity();
  }, [loadCards, loadActivity]);

  return (
    <div className="app-shell">
      <header className={header.header}>
        <div className={`container ${header.headerInner}`}>
          <span className={header.brand}>
            Vyapar<span className={header.brandAI}>AI</span>
          </span>
          <span className={header.headerSpacer} />
          <button
            className={header.commandTrigger}
            onClick={openCommand}
            aria-label="Open command bar"
          >
            Ask or command
            <Kbd>{navigator.platform.includes('Mac') ? '⌘K' : 'Ctrl K'}</Kbd>
          </button>
        </div>
      </header>

      <Dashboard />
      <CommandBar />

      <div style={{ display: 'none' }}>{APP_CONFIG.brand.tagline}</div>
    </div>
  );
}
