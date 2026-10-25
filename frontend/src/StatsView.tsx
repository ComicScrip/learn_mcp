import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Rectangle,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type BarShapeProps,
  type TooltipContentProps,
} from "recharts";
import type { CallTool, Stats } from "./types";

const SERIES = [
  { key: "done", label: "Effectuées", color: "var(--series-done)" },
  { key: "pending", label: "À faire", color: "var(--series-pending)" },
] as const;

export function StatsView({ stats, call }: { stats: Stats; call: CallTool }) {
  const [showTable, setShowTable] = useState(false);
  const { done, pending } = stats.totals;
  const total = done + pending;
  const rate = total ? Math.round((done / total) * 100) : 0;

  // Changer de période = rappeler show_stats avec d'autres arguments.
  const go = (period: Stats["period"], offset: number) => call("show_stats", { period, offset });

  return (
    <main className="card">
      <header className="header">
        <h2>Statistiques</h2>
        <button className="link" onClick={() => call("show_todos")}>
          ← Mes tâches
        </button>
      </header>

      <div className="toolbar">
        <div className="segmented" role="group" aria-label="Période">
          {(["week", "month"] as const).map((p) => (
            <button key={p} aria-pressed={stats.period === p} onClick={() => go(p, 0)}>
              {p === "week" ? "Semaine" : "Mois"}
            </button>
          ))}
        </div>
        <div className="nav">
          <button aria-label="Période précédente" onClick={() => go(stats.period, stats.offset - 1)}>
            ‹
          </button>
          <span className="period-title">{stats.title}</span>
          <button
            aria-label="Période suivante"
            disabled={stats.offset >= 0}
            onClick={() => go(stats.period, stats.offset + 1)}
          >
            ›
          </button>
        </div>
      </div>

      <div className="tiles">
        <Tile label="Effectuées" value={done} swatch="var(--series-done)" />
        <Tile label="À faire" value={pending} swatch="var(--series-pending)" />
        <Tile label="Taux de réalisation" value={`${rate} %`} />
      </div>

      <ul className="legend">
        {SERIES.map((s) => (
          <li key={s.key}>
            <i style={{ background: s.color }} />
            {s.label}
          </li>
        ))}
      </ul>

      <div className="chart">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={stats.buckets} margin={{ top: 8, right: 4, bottom: 0, left: -20 }}>
            <CartesianGrid vertical={false} stroke="var(--grid)" />
            <XAxis
              dataKey="label"
              tickLine={false}
              axisLine={{ stroke: "var(--axis)" }}
              tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
            />
            <YAxis
              allowDecimals={false}
              tickLine={false}
              axisLine={false}
              tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
            />
            <Tooltip content={ChartTooltip} cursor={{ fill: "var(--hover)" }} />
            {/* Barres empilées : "Effectuées" en bas, "À faire" au-dessus.
                Le contour de la couleur du fond crée l'espace de 2px entre segments. */}
            <Bar
              dataKey="done"
              stackId="t"
              fill="var(--series-done)"
              stroke="var(--surface)"
              strokeWidth={2}
              maxBarSize={36}
              shape={TopRounded("pending")}
            />
            <Bar
              dataKey="pending"
              stackId="t"
              fill="var(--series-pending)"
              stroke="var(--surface)"
              strokeWidth={2}
              maxBarSize={36}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <button className="link small" onClick={() => setShowTable(!showTable)}>
        {showTable ? "Masquer le tableau" : "Voir le tableau"}
      </button>
      {showTable && (
        <table>
          <thead>
            <tr>
              <th>{stats.period === "week" ? "Jour" : "Semaine"}</th>
              <th>Effectuées</th>
              <th>À faire</th>
            </tr>
          </thead>
          <tbody>
            {stats.buckets.map((b) => (
              <tr key={b.label}>
                <td>{b.label}</td>
                <td>{b.done}</td>
                <td>{b.pending}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}

function Tile({ label, value, swatch }: { label: string; value: number | string; swatch?: string }) {
  return (
    <div className="tile">
      <span className="tile-label">
        {swatch && <i style={{ background: swatch }} />}
        {label}
      </span>
      <strong>{value}</strong>
    </div>
  );
}

// Le segment du bas n'est arrondi en haut que s'il n'y a rien au-dessus de lui.
function TopRounded(above: "pending") {
  return (props: BarShapeProps) => (
    <Rectangle {...props} radius={props.payload?.[above] ? 0 : [4, 4, 0, 0]} />
  );
}

function ChartTooltip({ active, payload, label }: TooltipContentProps) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload as Stats["buckets"][number];
  return (
    <div className="tooltip">
      <strong>{label}</strong>
      {SERIES.map((s) => (
        <div key={s.key} className="tooltip-row">
          <i style={{ background: s.color }} />
          <span>{s.label}</span>
          <b>{row[s.key]}</b>
        </div>
      ))}
    </div>
  );
}
