import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";
import { api } from "../lib/api";
import { fmtT } from "../lib/format";
import { QueryError } from "../components/Insights";

export default function Reserves() {
  const mines = useQuery({ queryKey: ["mines"], queryFn: api.mines });
  const rows = useQuery({
    queryKey: ["reserves-all", mines.data?.length], enabled: !!mines.data,
    queryFn: async () => (await Promise.all(mines.data!.map((m) => api.reserves(m.code).catch(() => null)))).filter(Boolean),
  });
  const d = rows.data ?? [];
  const ax = { axisLabel: { color: "#94a3b8" } };
  const option: any = {
    backgroundColor: "transparent", tooltip: { trigger: "axis" }, legend: { textStyle: { color: "#94a3b8" } },
    grid: { left: 60, right: 16, top: 36, bottom: 28 },
    xAxis: { type: "category", data: d.map((r) => r!.mine), ...ax },
    yAxis: { type: "value", name: "tonnes", ...ax, splitLine: { lineStyle: { color: "#1e293b" } } },
    series: [["P10 (pessimistic)", "p10_t", "#64748b"], ["P50", "p50_t", "#38bdf8"], ["P90 (optimistic)", "p90_t", "#22c55e"]]
      .map(([name, key, color]) => ({ name, type: "bar", itemStyle: { color }, data: d.map((r: any) => Math.round(r[key])) })),
  };

  const selectedMine = d.length > 0 ? d[0] : null;

  const histOption: any = selectedMine ? {
    backgroundColor: "transparent", tooltip: { trigger: "axis" },
    title: { text: `Grade distribution (${selectedMine.mine})`, textStyle: { color: "#94a3b8", fontSize: 14 } },
    grid: { left: 60, right: 16, top: 36, bottom: 28 },
    xAxis: { type: "category", data: selectedMine.grade_hist_x.map((x: number) => x.toFixed(1) + "%"), ...ax, name: "Mn %" },
    yAxis: { type: "value", name: "tonnes", ...ax, splitLine: { lineStyle: { color: "#1e293b" } } },
    series: [{ type: "bar", data: selectedMine.grade_hist_y, itemStyle: { color: "#8b5cf6" }, barWidth: "90%" }]
  } : {};

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Reserve estimates (kriging, approximate P10–P90)</h2>
      <QueryError error={mines.error ?? rows.error} what="reserves" />
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4"><ReactECharts option={option} style={{ height: 360 }} /></div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4"><ReactECharts option={histOption} style={{ height: 360 }} /></div>
      </div>

      <table className="w-full text-left text-sm">
        <thead className="text-slate-400"><tr><th>Mine</th><th>P10</th><th>P50</th><th>P90</th><th>Mean ore grade</th><th>Cut-off</th></tr></thead>
        <tbody>{d.map((r: any) => (
          <tr key={r.mine} className="border-t border-slate-800">
            <td className="py-2">{r.mine}</td><td>{fmtT(r.p10_t)}</td><td>{fmtT(r.p50_t)}</td><td>{fmtT(r.p90_t)}</td>
            <td>{r.mean_grade.toFixed(1)}% Mn</td><td>{r.cutoff}% Mn</td></tr>))}
        </tbody>
      </table>
    </div>
  );
}
