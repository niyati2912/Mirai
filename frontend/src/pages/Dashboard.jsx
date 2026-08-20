import { useEffect, useState, useCallback } from "react";
import Panel from "../components/Panel";
import ForecastChart from "../components/ForecastChart";
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import { getForecastData } from "../services/api";
import { formatNumber, formatPercent, formatDate } from "../utils/formatters";

export default function Forecast() {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading");

  const load = useCallback(() => {
    setStatus("loading");
    getForecastData()
      .then((res) => {
        setData(res);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (status === "loading") {
    return (
      <main className="page">
        <LoadingState />
      </main>
    );
  }

  if (status === "error") {
    return (
      <main className="page">
        <ErrorState onRetry={load} />
      </main>
    );
  }

  const { series, holdout_start, holdout_end, metrics, notes } = data;

  return (
    <main className="page">
      <div className="page-header">
        <h1 className="page-title">Actual vs Predicted Economic Stress</h1>
        <p className="page-subtitle">
          Predictions are evaluated on a chronological holdout period. The target is ESS three
          months into the future.
        </p>
      </div>

      <Panel
        title="ESS Time-Series Forecast"
        controls={
          holdout_start && holdout_end ? (
            <span className="mono" style={{ fontSize: 11, color: "var(--text-dim)" }}>
              Holdout: {formatDate(holdout_start)} – {formatDate(holdout_end)}
            </span>
          ) : undefined
        }
      >
        <ForecastChart data={series} />
      </Panel>

      <div style={{ marginTop: "var(--gutter)" }} className="two-col-grid">
        <Panel title="Holdout Error Metrics">
          {metrics && metrics.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>3M Forward RMSE</th>
                  <th>Δ vs Baseline</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((row) => (
                  <tr key={row.model}>
                    <td>{row.model}</td>
                    <td>{formatNumber(row.rmse_3m_forward, 3)}</td>
                    <td className={row.delta_vs_baseline_pct > 0 ? "value-chip positive" : "value-chip negative"}>
                      {formatPercent(row.delta_vs_baseline_pct)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState message="NO HOLDOUT METRICS AVAILABLE" />
          )}
        </Panel>

        <Panel title="Model Performance Notes">
          {notes ? (
            <p className="notes-text">
              The best performing model on this holdout is <strong>{notes.best_model}</strong>{" "}
              with an RMSE of <strong>{formatNumber(notes.best_model_rmse, 3)}</strong>.{" "}
              {notes.improvement_vs_baseline_pct !== undefined && notes.improvement_vs_baseline_pct !== null && (
                <>
                  Compared with the persistence baseline, it improved RMSE by{" "}
                  <strong>{formatPercent(notes.improvement_vs_baseline_pct)}</strong>.{" "}
                </>
              )}
              {notes.behavioral_improved !== undefined && (
                <>
                  Behavioral signals{" "}
                  <strong>{notes.behavioral_improved ? "did" : "did not"}</strong> provide a
                  measurable RMSE improvement over the conventional-only model
                  {notes.behavioral_delta_pct !== undefined && notes.behavioral_delta_pct !== null && (
                    <> ({formatPercent(notes.behavioral_delta_pct)}).</>
                  )}
                </>
              )}
            </p>
          ) : (
            <EmptyState message="NO MODEL NOTES AVAILABLE" />
          )}
        </Panel>
      </div>
    </main>
  );
}
