/* ── Financial profile state ─────────────────────────────────────────── */

import { create } from 'zustand';
import type { FinancialProfile } from '@/lib/types';
import { getProfile, updateProfile } from '@/lib/api';

interface ProfileStore {
  profile: FinancialProfile | null;
  isLoading: boolean;

  fetchProfile: (sessionId: string) => Promise<void>;
  updateField: (sessionId: string, update: Partial<FinancialProfile>) => Promise<void>;
}

export const useFinancialProfileStore = create<ProfileStore>((set) => ({
// Also export as useProfileStore for backward compat

  profile: null,
  isLoading: false,

  fetchProfile: async (sessionId) => {
    set({ isLoading: true });
    try {
      const profile = await getProfile(sessionId);
      set({ profile, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  updateField: async (sessionId, update) => {
    try {
      const profile = await updateProfile(sessionId, update);
      set({ profile });
    } catch (err) {
      console.error('Profile update failed:', err);
    }
  },
}));

export const useProfileStore = useFinancialProfileStore;
