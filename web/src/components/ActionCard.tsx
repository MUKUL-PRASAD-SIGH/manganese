import { useMutation } from "@tanstack/react-query";
import { api, type Action, type Risk } from "../lib/api";
import { fmtT } from "../lib/format";

const ICON: Record<string, string> = { blast_advance: "💥", maintenance: "🔧", redeploy: "🚜" };

export default function ActionCard({ a, horizon = 7, onResult }:
  { a: Action; horizon?: number; onResult?: (r: Risk) => void }) {
  const sim = useMutation({ mutationFn: () => api.simulate(a.id, horizon), onSuccess: (r) => onResult?.(r) });
  const steps = (a.detail.steps as string[] | undefined) ?? [];
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="flex items-start gap-3">
        <span className="text-xl">{ICON[a.kind] ?? "⚙️"}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold leading-snug">{a.title}</h4>
            <span className="ml-auto rounded bg-slate-800 px-1.5 py-0.5 text-[10px] uppercase text-slate-400">{a.mine}</span>
          </div>
          <p className="mt-1 text-sm text-emerald-300">+{fmtT(a.expected_tonnes)} expected recovery</p>
          {steps.length > 0 && (
            <ul className="mt-2 list-disc pl-5 text-sm text-slate-400">{steps.map((s) => <li key={s}>{s}</li>)}</ul>
          )}
          <div className="mt-3 flex items-center gap-3">
            <div className="h-1.5 w-24 rounded bg-slate-800">
              <div className="h-1.5 rounded bg-sky-400" style={{ width: `${a.confidence * 100}%` }} />
            </div>
            <span className="text-xs text-slate-400">{Math.round(a.confidence * 100)}% confidence</span>
            {onResult && (
              <button onClick={() => sim.mutate()} disabled={sim.isPending}
                className="ml-auto rounded-lg bg-emerald-500 px-3 py-1.5 text-sm font-semibold text-slate-950 hover:bg-emerald-400 disabled:opacity-60 print:hidden">
                {sim.isPending ? "Simulating…" : "Simulate impact"}
              </button>
            )}
          </div>
          {sim.isError && (
            <p className="mt-2 text-xs text-red-300">Simulation failed: {(sim.error as Error).message}</p>
          )}
        </div>
      </div>
    </article>
  );
}
