import ReactECharts from "echarts-for-react";
import type { BandPoint } from "../lib/api";

export default function FanChart({ band, after }: { band: BandPoint[]; after?: BandPoint[] }) {
  const axis = { axisLabel: { color: "#94a3b8" } };
  const option: any = {
    backgroundColor: "transparent",
    grid: { left: 52, right: 44, top: 32, bottom: 28 },
    legend: { top: 0, textStyle: { color: "#94a3b8" }, data: ["Plan", "Expected", "After action", "Rain (mm)"] },
    tooltip: {
      trigger: "axis",
      formatter: (p: any) => {
        const b = band[p[0].dataIndex];
        const a = after?.[p[0].dataIndex];
        return `${b.date}<br/>Plan ${b.planned.toFixed(0)} t<br/>Expected ${b.q50.toFixed(0)} t`
          + `<br/>Range ${b.q10.toFixed(0)}–${b.q90.toFixed(0)} t<br/>Rain ${b.rain_mm.toFixed(0)} mm`
          + (a ? `<br/><b style="color:#22c55e">After action ${a.q50.toFixed(0)} t</b>` : "");
      },
    },
    xAxis: { type: "category", data: band.map((b) => b.date.slice(5)), ...axis },
    yAxis: [
      { type: "value", name: "t/day", ...axis, splitLine: { lineStyle: { color: "#1e293b" } },
        min: (v: { min: number }) => Math.floor(v.min * 0.85) },
      { type: "value", inverse: true, max: (v: { max: number }) => Math.max(80, v.max * 2.2),
        ...axis, splitLine: { show: false } },
    ],
    series: [
      { name: "_base", type: "line", stack: "band", data: band.map((b) => b.q10), symbol: "none", lineStyle: { opacity: 0 } },
      { name: "_band", type: "line", stack: "band", data: band.map((b) => b.q90 - b.q10), symbol: "none",
        lineStyle: { opacity: 0 }, areaStyle: { color: "rgba(245,158,11,0.22)" } },
      { name: "Rain (mm)", type: "bar", yAxisIndex: 1, data: band.map((b) => b.rain_mm),
        itemStyle: { color: "rgba(56,189,248,0.45)" }, barWidth: "40%" },
      { name: "Plan", type: "line", data: band.map((b) => b.planned), symbol: "none",
        lineStyle: { type: "dashed", color: "#94a3b8" } },
      { name: "Expected", type: "line", smooth: true, data: band.map((b) => b.q50), symbol: "circle",
        lineStyle: { color: "#f59e0b", width: 3 }, itemStyle: { color: "#f59e0b" } },
      ...(after ? [{ name: "After action", type: "line", smooth: true, data: after.map((b) => b.q50),
        symbol: "circle", lineStyle: { color: "#22c55e", width: 3 }, itemStyle: { color: "#22c55e" } }] : []),
    ],
  };
  return <ReactECharts option={option} notMerge style={{ height: 320 }} />;
}
