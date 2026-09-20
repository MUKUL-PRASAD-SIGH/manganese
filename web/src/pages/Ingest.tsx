import { useState } from "react";
import { api } from "../lib/api";

const KINDS = {
  production: "mine_code,date,planned_t,actual_t",
  weather: "mine_code,date,rain_mm",
  blasts: "mine_code,date,delayed",
  equipment: "mine_code,unit_code,date,available_hours,scheduled_hours,breakdown",
  drillholes: "mine_code,hole_code,lat,lon,collar_z,from_m,to_m,mn_pct,fe_pct",
} as const;

export default function Ingest() {
  const [kind, setKind] = useState<keyof typeof KINDS>("production");
  const [msg, setMsg] = useState("");
  const upload = async (f?: File) => {
    if (!f) return;
    setMsg("Uploading…");
    try { const r = await api.ingest(kind, f); setMsg(`✓ ${r.rows} rows loaded (${r.date_min} → ${r.date_max}). Forecasts refreshed.`); }
    catch (e) { setMsg(`✗ ${(e as Error).message}`); }
  };
  return (
    <div className="max-w-2xl space-y-4">
      <h2 className="text-lg font-semibold">Data adapter: bring your own MOIL data</h2>
      <select value={kind} onChange={(e) => setKind(e.target.value as any)} className="rounded bg-slate-800 px-3 py-2">
        {Object.keys(KINDS).map((k) => <option key={k}>{k}</option>)}
      </select>
      <p className="text-sm text-slate-400">Required columns: <code className="text-sky-300">{KINDS[kind]}</code></p>
      <label onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files[0]); }}
        className="flex h-40 cursor-pointer items-center justify-center rounded-2xl border-2 border-dashed border-slate-600 text-slate-400 hover:border-sky-400">
        Drop CSV here or click to choose
        <input type="file" accept=".csv" hidden onChange={(e) => upload(e.target.files?.[0])} />
      </label>
      {msg && <p className="text-sm">{msg}</p>}
    </div>
  );
}
