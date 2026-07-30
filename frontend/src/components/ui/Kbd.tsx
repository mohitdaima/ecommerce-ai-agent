import styles from './ui.module.css';

/** Renders a keyboard key hint, e.g. <Kbd>A</Kbd>. */
export function Kbd({ children }: { children: string }) {
  return <kbd className={styles.kbd}>{children}</kbd>;
}
