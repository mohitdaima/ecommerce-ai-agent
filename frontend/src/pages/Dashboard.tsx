import { MorningSummary } from '@/components/dashboard/MorningSummary';
import { NeedsApproval } from '@/components/dashboard/NeedsApproval';
import { DoneForYou } from '@/components/dashboard/DoneForYou';
import { Watching } from '@/components/dashboard/Watching';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';

/**
 * The new HOME. Layout per spec:
 *   Top     — Morning Summary
 *   Middle  — Needs Your Approval
 *   Bottom  — Done For You / Watching / Activity Feed
 * Chat is no longer here; it lives in the command bar.
 */
export function Dashboard() {
  return (
    <main className="container">
      <MorningSummary />
      <NeedsApproval />
      <DoneForYou />
      <Watching />
      <ActivityFeed />
      <div style={{ height: 'var(--space-10)' }} />
    </main>
  );
}
