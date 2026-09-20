import { NavLink, Route, Routes } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "./lib/api";
import Actions from "./pages/Actions";
import Ingest from "./pages/Ingest";
import Overview from "./pages/Overview";
import Reserves from "./pages/Reserves";

const link = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-1.5 text-sm ${isActive ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white"}`;

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
        {health.data?.data_mode === "demo" && (
          <span className="ml-auto rounded-full bg-amber-500/15 px-3 py-1 text-xs font-semibold text-amber-300 ring-1 ring-amber-500/40">
            SYNTHETIC DEMO DATA
          </span>
        )}
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
