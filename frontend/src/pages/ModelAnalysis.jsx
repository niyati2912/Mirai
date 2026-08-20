import { useMemo } from "react";
import {
Bar,
BarChart,
CartesianGrid,
ResponsiveContainer,
Tooltip,
XAxis,
YAxis,
} from "recharts";

import Panel from "../components/Panel";

function format(value, digits = 3) {
return Number.isFinite(Number(value))
? Number(value).toFixed(digits)
: "—";
}

export default function ModelAnalysis({ data }) {
const { metricRows } = data;

const bestByRMSE = useMemo(() => {
const usable = metricRows.filter(
    (row) => Number.isFinite(row.RMSE)
);

if (!usable.length) return null;

return [...usable].sort(
    (a, b) => a.RMSE - b.RMSE
)[0];
}, [metricRows]);

const comparisonData = metricRows.map(
(row) => ({
    name:
    row.name.length > 18
        ? row.name.slice(0, 18) + "…"
        : row.name,
    fullName: row.name,
    MAE: row.MAE,
    RMSE: row.RMSE,
    R2: row.R2,
})
);

return (
<div className="page">
    <section className="page-intro">
    <div>
        <div className="eyebrow">
        EXPERIMENT EVALUATION
        </div>

        <h1>Model Analysis</h1>

        <p>
        Comparison of forecasting experiments
        using chronological out-of-sample
        evaluation.
        </p>
    </div>

    <div className="analysis-callout">
        <span>BEST RMSE</span>

        <strong>
        {bestByRMSE
            ? bestByRMSE.name
            : "—"}
        </strong>
    </div>
    </section>

    {!metricRows.length ? (
    <Panel
        title="MODEL METRICS UNAVAILABLE"
    >
        <div className="empty-state">
        <h3>
            No metrics could be loaded.
        </h3>

        <p>
            Check
            <code>
            model_metrics.csv
            </code>
            in your public data folder.
        </p>
        </div>
    </Panel>
    ) : (
    <>
        <section className="experiment-table-panel">
        <Panel
            title="FORECASTING EXPERIMENTS"
            subtitle="Actual values loaded from model_metrics.csv"
        >
            <div className="table-wrap">
            <table className="data-table">
                <thead>
                <tr>
                    <th>EXPERIMENT</th>
                    <th>MAE ↓</th>
                    <th>RMSE ↓</th>
                    <th>R² ↑</th>
                    <th>STATUS</th>
                </tr>
                </thead>

                <tbody>
                {metricRows.map(
                    (row) => {
                    const isBest =
                        bestByRMSE?.id === row.id;

                    return (
                        <tr key={row.id}>
                        <td>
                            <strong>
                            {row.name}
                            </strong>
                        </td>

                        <td>
                            {format(
                            row.MAE
                            )}
                        </td>

                        <td className="metric-highlight">
                            {format(
                            row.RMSE
                            )}
                        </td>

                        <td>
                            {format(
                            row.R2
                            )}
                        </td>

                        <td>
                            {isBest ? (
                            <span className="table-status best">
                                LOWEST RMSE
                            </span>
                            ) : (
                            <span className="table-status">
                                EVALUATED
                            </span>
                            )}
                        </td>
                        </tr>
                    );
                    }
                )}
                </tbody>
            </table>
            </div>
        </Panel>
        </section>

        <section className="model-chart-grid">
        <Panel
            title="RMSE COMPARISON"
            subtitle="Lower is better"
        >
            <div className="bar-chart-wrap">
            <ResponsiveContainer
                width="100%"
                height="100%"
            >
                <BarChart
                data={comparisonData}
                margin={{
                    top: 15,
                    right: 12,
                    left: -12,
                    bottom: 0,
                }}
                >
                <CartesianGrid
                    stroke="#202a35"
                    strokeDasharray="3 5"
                    vertical={false}
                />

                <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{
                    fill: "#667382",
                    fontSize: 9,
                    fontFamily:
                        "JetBrains Mono",
                    }}
                />

                <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{
                    fill: "#667382",
                    fontSize: 10,
                    fontFamily:
                        "JetBrains Mono",
                    }}
                />

                <Tooltip
                    contentStyle={{
                    background: "#111820",
                    border:
                        "1px solid #26313d",
                    borderRadius: 4,
                    }}
                />

                <Bar
                    dataKey="RMSE"
                    fill="#8ed1ff"
                    radius={[2, 2, 0, 0]}
                />
                </BarChart>
            </ResponsiveContainer>
            </div>
        </Panel>

        <Panel
            title="MAE COMPARISON"
            subtitle="Average absolute error"
        >
            <div className="bar-chart-wrap">
            <ResponsiveContainer
                width="100%"
                height="100%"
            >
                <BarChart
                data={comparisonData}
                margin={{
                    top: 15,
                    right: 12,
                    left: -12,
                    bottom: 0,
                }}
                >
                <CartesianGrid
                    stroke="#202a35"
                    strokeDasharray="3 5"
                    vertical={false}
                />

                <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{
                    fill: "#667382",
                    fontSize: 9,
                    fontFamily:
                        "JetBrains Mono",
                    }}
                />

                <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{
                    fill: "#667382",
                    fontSize: 10,
                    fontFamily:
                        "JetBrains Mono",
                    }}
                />

                <Tooltip
                    contentStyle={{
                    background: "#111820",
                    border:
                        "1px solid #26313d",
                    borderRadius: 4,
                    }}
                />

                <Bar
                    dataKey="MAE"
                    fill="#f3b85b"
                    radius={[2, 2, 0, 0]}
                />
                </BarChart>
            </ResponsiveContainer>
            </div>
        </Panel>
        </section>

        <section className="model-conclusion-grid">
        <Panel
            title="EXPERIMENT DESIGN"
        >
            <div className="experiment-design">
            <div>
                <span>01</span>

                <strong>
                Persistence Baseline
                </strong>

                <p>
                Uses the current ESS as a
                simple benchmark for future
                ESS.
                </p>
            </div>

            <div>
                <span>02</span>

                <strong>
                Conventional Model
                </strong>

                <p>
                Uses conventional economic and
                energy-related indicators.
                </p>
            </div>

            <div>
                <span>03</span>

                <strong>
                Conventional + Behavioral
                </strong>

                <p>
                Tests whether search-based
                behavioral signals add
                predictive information.
                </p>
            </div>
            </div>
        </Panel>

        <Panel
            title="INTERPRETATION"
        >
            <div className="model-interpretation">
            <strong>
                Results should be interpreted as
                predictive evidence, not causal
                proof.
            </strong>

            <p>
                The experiment tests whether the
                additional behavioral feature set
                improves forecasting metrics
                relative to conventional inputs.
                The dashboard displays the actual
                results generated by the current
                pipeline rather than assuming
                improvement.
            </p>

            <span>
                CHRONOLOGICAL TRAIN → TEST SPLIT
            </span>
            </div>
        </Panel>
        </section>
    </>
    )}
</div>
);
}