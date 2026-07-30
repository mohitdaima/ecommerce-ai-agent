import { create } from 'zustand';

/* Ephemeral UI state kept out of the domain stores: which card is focused
   (for keyboard nav) and whether the command bar is open. */

interface UiState {
  selectedCardId: string | null;
  commandOpen: boolean;
  select: (id: string | null) => void;
  openCommand: () => void;
  closeCommand: () => void;
  toggleCommand: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  selectedCardId: null,
  commandOpen: false,
  select: (id) => set({ selectedCardId: id }),
  openCommand: () => set({ commandOpen: true }),
  closeCommand: () => set({ commandOpen: false }),
  toggleCommand: () => set((s) => ({ commandOpen: !s.commandOpen })),
}));
