import EmptyState from "./EmptyState";
import { formatNumber } from "../utils/formatters";

const CATEGORY_LABELS = {
  macro: "Macroeconomic",
  behavioral: "Behavioral",
  energy: "Energy",
};

// Rendered in this order to match the Stitch reference.
const ORDER = ["macro", "behavioral", "energy"];

export default function SignalBreakdown({ breakdown }) {
  if (!breakdown) {
    return <EmptyState message="NO SIGNAL DATA AVAILABLE" />;
  }

  return (
    <div>
      {ORDER.filter((key) => breakdown[key]).map((key) => {
        const { value, weight } = breakdown[key];
        return (
          <div className="signal-row" key={key}>
            <div className="signal-row-header">
              <span className="signal-row-name">{CATEGORY_LABELS[key]}</span>
              <span className="signal-row-weight">{Math.round(weight * 100)}% weight</span>
            </div>
            <div className="signal-bar-track">
              <div
                className={`signal-bar-fill ${key}`}
                style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
              />
            </div>
            <div className="signal-row-value mono" style={{ marginTop: 4, fontSize: 12 }}>
              {formatNumber(value)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
