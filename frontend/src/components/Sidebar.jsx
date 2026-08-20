import { stressStatus } from "../utils/formatters";

const LABELS = {
  low: "Low Stress",
  moderate: "Moderate Stress",
  high: "High Stress",
};

export default function StatusBadge({ ess }) {
  const status = stressStatus(ess);
  if (!status) {
    return (
      <span className="status-badge">
        <span className="status-dot" style={{ background: "var(--text-dim)" }} />
        No Data
      </span>
    );
  }
  return (
    <span className={`status-badge ${status}`}>
      <span className="status-dot" />
      {LABELS[status]}
    </span>
  );
}
