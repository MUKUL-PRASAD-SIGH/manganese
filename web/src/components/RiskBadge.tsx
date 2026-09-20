import type { Level } from "../lib/api";

const C: Record<Level, string> = {
  green: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/40",
  amber: "bg-amber-500/15 text-amber-300 ring-amber-500/40",
  red: "bg-red-500/15 text-red-300 ring-red-500/40",
};
export default function RiskBadge({ level }: { level: Level }) {
  return <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ring-1 ${C[level]}`}>{level}</span>;
}
