import { create } from 'zustand';
import type { ActivityEntry } from '@/types';
import { actionCardService } from '@/services/actionCardService';

interface ActivityState {
  entries: ActivityEntry[];
  loaded: boolean;
  load: () => Promise<void>;
  /** Append-only: prepend a new entry (ledger never rewrites history). */
  record: (entry: ActivityEntry) => void;
}

export const useActivityStore = create<ActivityState>((set) => ({
  entries: [],
  loaded: false,
  load: async () => {
    const entries = await actionCardService.fetchActivity();
    set({ entries, loaded: true });
  },
  record: (entry) =>
    set((state) => ({ entries: [entry, ...state.entries] })),
}));
