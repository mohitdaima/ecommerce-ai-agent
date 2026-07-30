import { APP_CONFIG, IMPACT_DIRECTION } from '@/config/app.config';
import type { Impact } from '@/types';

/* Pure formatting helpers. No component may format money/time inline. */

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat(APP_CONFIG.currency.locale, {
    style: 'currency',
    currency: APP_CONFIG.currency.code,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatImpact(impact: Impact): string {
  const dir = IMPACT_DIRECTION[impact.direction].label;
  return `${dir} ${formatCurrency(impact.currencyValue)}`;
}

export function formatMinutesSaved(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const hours = minutes / 60;
  const rounded = Math.round(hours * 10) / 10;
  return `${rounded} hr${rounded === 1 ? '' : 's'}`;
}

export function formatRelativeTime(iso: string, now: Date = new Date()): string {
  const then = new Date(iso).getTime();
  const diffMs = now.getTime() - then;
  const min = Math.round(diffMs / 60000);
  if (min < 1) return 'just now';
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const days = Math.round(hr / 24);
  return `${days}d ago`;
}
