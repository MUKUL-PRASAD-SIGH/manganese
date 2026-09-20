export const fmtT = (n: number) =>
  n >= 1e6 ? `${(n / 1e6).toFixed(2)} Mt` : n >= 1e3 ? `${(n / 1e3).toFixed(1)} kt` : `${Math.round(n)} t`;
export const LEVEL_HEX = { green: "#22c55e", amber: "#f59e0b", red: "#ef4444" } as const;
