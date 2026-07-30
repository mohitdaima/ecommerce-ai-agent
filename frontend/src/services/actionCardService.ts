import type { ActionCard, ActivityEntry } from '@/types';
import { MOCK_CARDS, MOCK_ACTIVITY } from './mockData';

/* =========================================================================
   Data-access seam. The app depends on this INTERFACE, never on a concrete
   source. Sprint 1 ships MockActionCardService; a later sprint drops in an
   HttpActionCardService (Flask API) with zero changes to the UI or stores.
   ========================================================================= */

export interface ActionCardService {
  fetchCards(): Promise<ActionCard[]>;
  fetchActivity(): Promise<ActivityEntry[]>;
  /** Reserved for Sprint 2: executes an approved card's ChangeSet. */
  execute?(card: ActionCard): Promise<{ ok: boolean }>;
}

class MockActionCardService implements ActionCardService {
  async fetchCards(): Promise<ActionCard[]> {
    return structuredClone(MOCK_CARDS);
  }

  async fetchActivity(): Promise<ActivityEntry[]> {
    return structuredClone(MOCK_ACTIVITY);
  }
}

/** Single shared instance the stores consume. */
export const actionCardService: ActionCardService = new MockActionCardService();
