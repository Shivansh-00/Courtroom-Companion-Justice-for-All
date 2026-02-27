'use client';

import { create } from 'zustand';

type PipelineEvent = {
  stage: string;
  progress: number;
  message: string;
};

type AppState = {
  token: string;
  role: string;
  pipeline: PipelineEvent[];
  setAuth: (token: string, role: string) => void;
  addEvent: (event: PipelineEvent) => void;
};

export const useAppStore = create<AppState>((set) => ({
  token: '',
  role: '',
  pipeline: [],
  setAuth: (token, role) => set({ token, role }),
  addEvent: (event) => set((state) => ({ pipeline: [...state.pipeline, event] })),
}));
