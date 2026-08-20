export default function MetricCard({ label, value, sub, subTone }) {
  return (
    <div className="metric-card">
      <div className="metric-card-label label-caps">{label}</div>
      <div className="metric-card-value mono">{value ?? "—"}</div>
      {sub && (
        <div className={`metric-card-sub ${subTone ? subTone : ""}`}>{sub}</div>
      )}
    </div>
  );
}
