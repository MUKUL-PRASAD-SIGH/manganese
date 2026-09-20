import { create } from "zustand";
import type { Risk } from "./lib/api";

interface State {
  mine: string; horizon: 7 | 14; sim: Risk | null;
  setMine: (m: string) => void; setHorizon: (h: 7 | 14) => void; setSim: (r: Risk | null) => void;
}
export const useStore = create<State>((set) => ({
  mine: "", horizon: 7, sim: null,
  setMine: (mine) => set({ mine }), setHorizon: (horizon) => set({ horizon }), setSim: (sim) => set({ sim }),
}));
