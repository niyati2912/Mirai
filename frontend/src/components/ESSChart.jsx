import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import EmptyState from "./EmptyState";
import { formatDate, formatNumber } from "../utils/formatters";

const SERIES = [
  { key: "actual", label: "Actual ESS", color: "var(--text)" },
  { key: "conventional", label: "Conventional", color: "var(--blue)" },
  { key: "conventional_behavioral", label: "Conv + Behavioral", color: "var(--amber)" },
];

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div
      style={{
        background: "var(--bg-elevated-high)",
        border: "1px solid var(--border-strong)",
        borderRadius: "var(--radius-sm)",
        padding: "8px 10px",
        fontFamily: "var(--font-mono)",
        fontSize: 12,
      }}
    >
      <div style={{ color: "var(--text-muted)", marginBottom: 4 }}>
        {formatDate(label, { year: "numeric", month: "short" })}
      </div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {formatNumber(p.value)}
        </div>
      ))}
    </div>
  );
}

export default function ForecastChart({ data }) {
  if (!data || data.length === 0) {
    return <EmptyState message="NO FORECAST DATA AVAILABLE" />;
  }

  // Only render series that actually have values in this dataset.
  const activeSeries = SERIES.filter((s) => data.some((row) => row[s.key] !== undefined && row[s.key] !== null));

  return (
    <ResponsiveContainer width="100%" height={340}>
      <LineChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
        <CartesianGrid stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="date"
          tickFormatter={(d) => formatDate(d)}
          stroke="var(--text-dim)"
          tick={{ fontFamily: "var(--font-mono)", fontSize: 11, fill: "var(--text-dim)" }}
          axisLine={{ stroke: "var(--border-strong)" }}
          tickLine={false}
          minTickGap={40}
        />
        <YAxis
          domain={[0, 100]}
          stroke="var(--text-dim)"
          tick={{ fontFamily: "var(--font-mono)", fontSize: 11, fill: "var(--text-dim)" }}
          axisLine={false}
          tickLine={false}
          width={32}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
        />
        {activeSeries.map((s) => (
          <Line
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.label}
            stroke={s.color}
            strokeWidth={1.75}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
