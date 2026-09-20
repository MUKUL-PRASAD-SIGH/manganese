import re

with open("web/src/pages/Reserves.tsx", "r") as f: text = f.read()

replacement = """  const option: any = {
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
"""

text = re.sub(r'  const option: any = \{.*?<div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4"><ReactECharts option=\{option\} style=\{\{ height: 360 \}\} /></div>', replacement, text, flags=re.DOTALL)
with open("web/src/pages/Reserves.tsx", "w") as f: f.write(text)
