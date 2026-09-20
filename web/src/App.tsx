import { NavLink, Route, Routes } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api, type Health } from "./lib/api";
import Actions from "./pages/Actions";
import Ingest from "./pages/Ingest";
import Overview from "./pages/Overview";
import Reserves from "./pages/Reserves";

const link = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-1.5 text-sm ${isActive ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white"}`;

/**
 * Honesty badge. Reports provenance per source rather than from a single
 * DATA_MODE flag: weather can be live while the ops data is still synthetic,
 * and a badge that hides in that case overclaims.
 */
function ProvenanceBadge({ health }: { health?: Health }) {
  if (!health) return null;
  const synth = health.synthetic_sources;
  const tooltip = health.provenance
    .map((p) => `${p.source}: ${p.mode}${p.detail ? ` — ${p.detail}` : ""}`)
    .join("\n");

  if (synth.length === 0) {
    return (
      <span title={tooltip}
        className="ml-auto rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-300 ring-1 ring-emerald-500/40">
        LIVE DATA
      </span>
    );
  }
  const all = synth.length === health.provenance.length;
  return (
    <span title={tooltip}
      className="ml-auto rounded-full bg-amber-500/15 px-3 py-1 text-xs font-semibold uppercase text-amber-300 ring-1 ring-amber-500/40">
      {all ? "Synthetic demo data" : `Synthetic: ${synth.join(" · ")}`}
    </span>
  );
}

export default function App() {
  const health = useQuery({ queryKey: ["health"], queryFn: api.health, refetchInterval: 60_000 });
  return (
    <div className="mx-auto max-w-[1400px] px-4 py-4">
      <header className="mb-4 flex items-center gap-3 print:hidden">
        <div className="text-lg font-bold">⛏ MOIL Manganese Copilot</div>
        <nav className="flex gap-1">
          <NavLink to="/" end className={link}>Command center</NavLink>
          <NavLink to="/reserves" className={link}>Reserves</NavLink>
          <NavLink to="/actions" className={link}>Actions</NavLink>
          <NavLink to="/ingest" className={link}>Data adapter</NavLink>
        </nav>
        <ProvenanceBadge health={health.data} />
      </header>
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/reserves" element={<Reserves />} />
        <Route path="/actions" element={<Actions />} />
        <Route path="/ingest" element={<Ingest />} />
      </Routes>
    </div>
  );
}
