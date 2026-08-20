import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import EmptyState from "./EmptyState";
import { formatDate, formatNumber } from "../utils/formatters";

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
      <div style={{ color: "var(--blue)" }}>ESS {formatNumber(payload[0].value)}</div>
    </div>
  );
}

export default function ESSChart({ data }) {
  if (!data || data.length === 0) {
    return <EmptyState message="NO ESS HISTORY AVAILABLE" />;
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
        <defs>
          <linearGradient id="essFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--blue-strong)" stopOpacity={0.25} />
            <stop offset="100%" stopColor="var(--blue-strong)" stopOpacity={0} />
          </linearGradient>
        </defs>
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
        <Area
          type="monotone"
          dataKey="ess"
          stroke="var(--blue)"
          strokeWidth={1.75}
          fill="url(#essFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
