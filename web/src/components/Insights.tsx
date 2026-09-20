import type { Driver } from "../lib/api";

export function LossSplit({ weather, equipment }: { weather: number; equipment: number }) {
  const total = Math.max(weather + equipment, 0.01);
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3">
      <div className="mb-2 text-xs uppercase tracking-wide text-slate-400">Why output drops</div>
      <div className="flex h-3 overflow-hidden rounded-full bg-slate-800">
        <div className="bg-sky-400" style={{ width: `${(weather / total) * 100}%` }} />
        <div className="bg-amber-400" style={{ width: `${(equipment / total) * 100}%` }} />
      </div>
      <div className="mt-2 flex justify-between text-xs text-slate-400">
        <span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-sky-400" />Weather {weather.toFixed(1)}%</span>
        <span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-amber-400" />Equipment {equipment.toFixed(1)}%</span>
      </div>
    </div>
  );
}

export function Drivers({ items }: { items: Driver[] }) {
  const max = Math.max(...items.map((d) => Math.abs(d.impact_pct)), 1);
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3">
      <div className="mb-2 text-xs uppercase tracking-wide text-slate-400">Top drags on output</div>
      {items.length === 0 && <p className="text-sm text-slate-500">No significant risk drivers.</p>}
      {items.map((d) => (
        <div key={d.label} className="mb-2">
          <div className="flex justify-between text-sm"><span>{d.label}</span><span className="text-red-300">{d.impact_pct}%</span></div>
          <div className="h-1.5 rounded bg-slate-800"><div className="h-1.5 rounded bg-red-400" style={{ width: `${(Math.abs(d.impact_pct) / max) * 100}%` }} /></div>
        </div>
      ))}
    </div>
  );
}

/** Minimal inline error surface for failed queries. */
export function QueryError({ error, what }: { error: unknown; what: string }) {
  if (!error) return null;
  const msg = error instanceof Error ? error.message : String(error);
  return (
    <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-1.5 text-xs text-red-300">
      Could not load {what}: {msg}
    </p>
  );
}
