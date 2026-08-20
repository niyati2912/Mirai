import { useEffect, useMemo, useState } from "react";
import Papa from "papaparse";
import {
Activity,
ArrowDownRight,
ArrowUpRight,
BarChart3,
BrainCircuit,
Database,
Gauge,
Layers3,
Loader2,
TrendingUp,
Zap,
} from "lucide-react";

import {
Area,
AreaChart,
Bar,
BarChart,
CartesianGrid,
Cell,
Legend,
Line,
LineChart,
ResponsiveContainer,
Tooltip,
XAxis,
YAxis,
} from "recharts";

const DATA_PATH = "/data/";

function loadCSV(file) {
return new Promise((resolve, reject) => {
Papa.parse(`${DATA_PATH}${file}`, {
    download: true,
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    complete: (results) => resolve(results.data),
    error: reject,
});
});
}

function formatNumber(value, digits = 1) {
if (value === null || value === undefined || Number.isNaN(Number(value))) {
return "—";
}

return Number(value).toFixed(digits);
}

function formatDate(value) {
if (!value) return "";

const date = new Date(value);

if (Number.isNaN(date.getTime())) {
return value;
}

return date.toLocaleDateString("en-US", {
month: "short",
year: "numeric",
});
}

function getStressStatus(score) {
if (score < 40) {
return {
    label: "Low Stress",
    className: "low",
};
}

if (score < 60) {
return {
    label: "Moderate Stress",
    className: "moderate",
};
}

return {
label: "High Stress",
className: "high",
};
}

function humanizeFeature(feature = "") {
return feature
.replace(/^fred_/, "")
.replace(/^eia_/, "")
.replace(/^trends_/, "")
.replace(/_Value/g, "")
.replace(/_/g, " ")
.replace(/\brolling3\b/g, "3M average")
.replace(/\brolling6\b/g, "6M average")
.replace(/\blag1\b/g, "previous month")
.replace(/\bpct change\b/g, "change")
.replace(/\brolling3 std\b/g, "3M volatility")
.replace(/\b\w/g, (char) => char.toUpperCase());
}

function MetricCard({ label, value, subtitle, icon, accent = "" }) {
return (
<div className={`metric-card ${accent}`}>
    <div className="metric-top">
    <span>{label}</span>
    <div className="metric-icon">{icon}</div>
    </div>

    <div className="metric-value">{value}</div>

    {subtitle && (
    <div className="metric-subtitle">
        {subtitle}
    </div>
    )}
</div>
);
}

function SectionTitle({ eyebrow, title, description }) {
return (
<div className="section-title">
    <div>
    {eyebrow && <div className="eyebrow">{eyebrow}</div>}
    <h2>{title}</h2>
    </div>

    {description && (
    <p>{description}</p>
    )}
</div>
);
}

export default function App() {
const [essData, setEssData] = useState([]);
const [metrics, setMetrics] = useState([]);
const [predictions, setPredictions] = useState([]);
const [importance, setImportance] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

useEffect(() => {
async function loadData() {
    try {
    setLoading(true);

    const [
        ess,
        metricData,
        predictionData,
        importanceData,
    ] = await Promise.all([
        loadCSV("ess_dataset.csv"),
        loadCSV("model_metrics.csv"),
        loadCSV("model_predictions.csv"),
        loadCSV("feature_importance.csv"),
    ]);

    setEssData(
        ess
        .filter((row) => row.Date)
        .sort(
            (a, b) =>
            new Date(a.Date) - new Date(b.Date)
        )
    );

    setMetrics(metricData);

    setPredictions(
        predictionData
        .filter((row) => row.Date)
        .sort(
            (a, b) =>
            new Date(a.Date) - new Date(b.Date)
        )
    );

    setImportance(
        importanceData
        .filter(
            (row) =>
            row.feature &&
            row.importance !== null &&
            row.importance !== undefined
        )
        .sort(
            (a, b) =>
            Number(b.importance) -
            Number(a.importance)
        )
    );
    } catch (err) {
    console.error(err);
    setError(
        "Could not load MIRAI data files. Check frontend/public/data/."
    );
    } finally {
    setLoading(false);
    }
}

loadData();
}, []);

const latestESS = useMemo(() => {
if (!essData.length) return null;
return essData[essData.length - 1];
}, [essData]);

const previousESS = useMemo(() => {
if (essData.length < 2) return null;
return essData[essData.length - 2];
}, [essData]);

const latestScore = Number(latestESS?.ESS);
const previousScore = Number(previousESS?.ESS);

const stressStatus = getStressStatus(latestScore);

const trend =
Number.isFinite(latestScore) &&
Number.isFinite(previousScore)
    ? latestScore - previousScore
    : 0;

const latestPrediction = predictions.length
? predictions[predictions.length - 1]
: null;

const conventionalMetric = metrics.find(
(item) =>
    item.Experiment === "conventional_only"
);

const fullMetric = metrics.find(
(item) =>
    item.Experiment ===
    "conventional_plus_behavioral"
);

const persistenceMetric = metrics.find(
(item) =>
    item.Experiment === "baseline"
);

const topImportance = importance.slice(0, 10);

const timelineData = essData.map((row) => ({
date: formatDate(row.Date),
ESS: Number(row.ESS),
Macro: Number(row.ESS_macro),
Energy: Number(row.ESS_energy),
Behavioral: Number(row.ESS_behavioral),
}));

const predictionChartData = predictions.map((row) => ({
date: formatDate(row.Date),
Actual: Number(row.Actual_ESS_target),
Conventional: Number(row.Conventional),
Full: Number(row.Conventional_Behavioral),
Persistence: Number(row.Persistence),
}));

if (loading) {
return (
    <div className="loading-screen">
    <Loader2 size={32} className="spin" />
    <p>Loading MIRAI intelligence data...</p>
    </div>
);
}

if (error) {
return (
    <div className="loading-screen error-screen">
    <h2>Data loading error</h2>
    <p>{error}</p>
    </div>
);
}

return (
<div className="app">
    <nav className="navbar">
    <div className="brand">
        <div className="brand-mark">
        <BrainCircuit size={22} />
        </div>

        <div>
        <h1>MIRAI</h1>
        <span>Economic Intelligence Platform</span>
        </div>
    </div>

    <div className="nav-links">
        <a href="#dashboard">Dashboard</a>
        <a href="#forecast">Forecast</a>
        <a href="#model">Model</a>
        <a href="#methodology">Methodology</a>
    </div>

    <div className="live-indicator">
        <span className="pulse" />
        Data Pipeline Complete
    </div>
    </nav>

    <main>
    <section
        id="dashboard"
        className="hero"
    >
        <div className="hero-copy">
        <div className="eyebrow">
            ECONOMIC SIGNAL INTELLIGENCE
        </div>

        <h2>
            Predicting tomorrow's economy
            <span> using today's signals.</span>
        </h2>

        <p>
            MIRAI combines macroeconomic, energy,
            and behavioral indicators into a
            project-specific Economic Stress Score
            and evaluates models for forecasting
            future economic stress.
        </p>

        <div className="hero-meta">
            <span>
            <Database size={16} />
            Multi-source economic data
            </span>

            <span>
            <BrainCircuit size={16} />
            Time-series machine learning
            </span>

            <span>
            <Gauge size={16} />
            3-month forecast horizon
            </span>
        </div>
        </div>

        <div className="hero-panel">
        <div className="hero-panel-label">
            Latest Economic Stress Score
        </div>

        <div className="hero-score">
            {formatNumber(latestScore)}
            <span>/100</span>
        </div>

        <div
            className={`status-pill ${stressStatus.className}`}
        >
            {stressStatus.label}
        </div>

        <div className="score-date">
            Latest observation ·{" "}
            {formatDate(latestESS?.Date)}
        </div>
        </div>
    </section>

    <section className="metrics-grid">
        <MetricCard
        label="Economic Stress Score"
        value={formatNumber(latestScore)}
        subtitle={stressStatus.label}
        icon={<Gauge size={20} />}
        accent="primary"
        />

        <MetricCard
        label="3-Month Forecast"
        value={
            latestPrediction
            ? formatNumber(
                latestPrediction.Full
                )
            : "—"
        }
        subtitle={
            latestPrediction
            ? `Latest test forecast · ${formatDate(
                latestPrediction.Date
                )}`
            : "No prediction available"
        }
        icon={<TrendingUp size={20} />}
        />

        <MetricCard
        label="Latest Trend"
        value={`${trend >= 0 ? "+" : ""}${formatNumber(
            trend
        )}`}
        subtitle={
            trend >= 0
            ? "Stress increased from prior observation"
            : "Stress decreased from prior observation"
        }
        icon={
            trend >= 0 ? (
            <ArrowUpRight size={20} />
            ) : (
            <ArrowDownRight size={20} />
            )
        }
        accent={trend >= 0 ? "risk" : "positive"}
        />

        <MetricCard
        label="Model RMSE"
        value={formatNumber(fullMetric?.RMSE, 2)}
        subtitle="Current Random Forest holdout result"
        icon={<Activity size={20} />}
        />
    </section>

    <section className="dashboard-grid">
        <div className="panel large-panel">
        <SectionTitle
            eyebrow="ECONOMIC STRESS"
            title="ESS Timeline"
            description="Historical project-specific economic stress score constructed from normalized indicators."
        />

        <div className="chart">
            <ResponsiveContainer
            width="100%"
            height={330}
            >
            <AreaChart data={timelineData}>
                <defs>
                <linearGradient
                    id="essGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                >
                    <stop
                    offset="0%"
                    stopColor="currentColor"
                    stopOpacity={0.35}
                    />
                    <stop
                    offset="100%"
                    stopColor="currentColor"
                    stopOpacity={0}
                    />
                </linearGradient>
                </defs>

                <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                />

                <XAxis
                dataKey="date"
                minTickGap={45}
                />

                <YAxis
                domain={["auto", "auto"]}
                />

                <Tooltip />

                <Area
                type="monotone"
                dataKey="ESS"
                strokeWidth={3}
                fill="url(#essGradient)"
                />
            </AreaChart>
            </ResponsiveContainer>
        </div>
        </div>

        <div className="panel component-panel">
        <SectionTitle
            eyebrow="ESS COMPONENTS"
            title="Signal Breakdown"
        />

        <div className="component-list">
            <div className="component-item">
            <div>
                <div className="component-name">
                <Layers3 size={18} />
                Macro
                </div>

                <span>
                Traditional economic indicators
                </span>
            </div>

            <strong>
                {formatNumber(latestESS?.ESS_macro)}
            </strong>
            </div>

            <div className="component-item">
            <div>
                <div className="component-name">
                <Zap size={18} />
                Energy
                </div>

                <span>
                Economic activity and energy pressure
                </span>
            </div>

            <strong>
                {formatNumber(latestESS?.ESS_energy)}
            </strong>
            </div>

            <div className="component-item">
            <div>
                <div className="component-name">
                <Activity size={18} />
                Behavioral
                </div>

                <span>
                Search-based behavioral signals
                </span>
            </div>

            <strong>
                {formatNumber(
                latestESS?.ESS_behavioral
                )}
            </strong>
            </div>
        </div>

        <div className="weight-box">
            <span>ESS Category Weights</span>

            <div className="weight-row">
            <span>Macro</span>
            <strong>45%</strong>
            </div>

            <div className="weight-row">
            <span>Energy</span>
            <strong>20%</strong>
            </div>

            <div className="weight-row">
            <span>Behavioral</span>
            <strong>35%</strong>
            </div>
        </div>
        </div>
    </section>

    <section
        id="forecast"
        className="panel forecast-panel"
    >
        <SectionTitle
        eyebrow="FORECASTING"
        title="Actual vs Predicted Economic Stress"
        description="Out-of-sample predictions from the chronological holdout period."
        />

        <div className="chart">
        <ResponsiveContainer
            width="100%"
            height={390}
        >
            <LineChart
            data={predictionChartData}
            >
            <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
            />

            <XAxis
                dataKey="date"
                minTickGap={40}
            />

            <YAxis
                domain={["auto", "auto"]}
            />

            <Tooltip />

            <Legend />

            <Line
                type="monotone"
                dataKey="Actual"
                strokeWidth={3}
                dot={false}
            />

            <Line
                type="monotone"
                dataKey="Conventional"
                strokeWidth={2}
                dot={false}
            />

            <Line
                type="monotone"
                dataKey="Full"
                name="Conventional + Behavioral"
                strokeWidth={2}
                dot={false}
                strokeDasharray="5 5"
            />
            </LineChart>
        </ResponsiveContainer>
        </div>

        <div className="forecast-note">
        The target is <strong>ESS three months into the future</strong>.
        Predictions are generated using historical features available
        at the observation date.
        </div>
    </section>

    <section
        id="model"
        className="model-section"
    >
        <SectionTitle
        eyebrow="MODEL ANALYSIS"
        title="Experiment Comparison"
        description="Performance is evaluated using chronological train/test separation rather than random shuffling."
        />

        <div className="comparison-grid">
        {metrics.map((metric) => {
            const isBaseline =
            metric.Experiment === "baseline";

            const title = isBaseline
            ? "Persistence Baseline"
            : metric.Experiment ===
                "conventional_only"
            ? "Conventional Model"
            : "Conventional + Behavioral";

            return (
            <div
                className="model-card"
                key={metric.Experiment}
            >
                <div className="model-card-header">
                <BarChart3 size={20} />

                <div>
                    <h3>{title}</h3>
                    <span>{metric.Model}</span>
                </div>
                </div>

                <div className="model-stats">
                <div>
                    <span>MAE</span>
                    <strong>
                    {formatNumber(metric.MAE, 3)}
                    </strong>
                </div>

                <div>
                    <span>RMSE</span>
                    <strong>
                    {formatNumber(metric.RMSE, 3)}
                    </strong>
                </div>

                <div>
                    <span>R²</span>
                    <strong>
                    {formatNumber(metric.R2, 3)}
                    </strong>
                </div>
                </div>

                <div className="feature-count">
                {metric.Feature_Count} usable predictors
                </div>
            </div>
            );
        })}
        </div>

        <div className="experiment-insight">
        <strong>Current experiment result:</strong>
        {" "}
        The Random Forest experiments improve MAE and RMSE
        compared with the persistence baseline. In the current
        run, the conventional and conventional + behavioral
        experiments produced identical metrics, so the dashboard
        does not claim behavioral improvement beyond what the
        actual results support.
        </div>
    </section>

    <section className="dashboard-grid importance-grid">
        <div className="panel large-panel">
        <SectionTitle
            eyebrow="EXPLAINABILITY"
            title="Top Random Forest Features"
            description="Feature importance shows which inputs the trained Random Forest relied on most. Importance does not imply causation."
        />

        <div className="chart">
            <ResponsiveContainer
            width="100%"
            height={400}
            >
            <BarChart
                data={topImportance}
                layout="vertical"
                margin={{
                left: 20,
                right: 30,
                }}
            >
                <CartesianGrid
                strokeDasharray="3 3"
                horizontal={false}
                />

                <XAxis
                type="number"
                />

                <YAxis
                type="category"
                dataKey="feature"
                width={230}
                tickFormatter={humanizeFeature}
                />

                <Tooltip
                formatter={(value) =>
                    formatNumber(value, 4)
                }
                labelFormatter={humanizeFeature}
                />

                <Bar
                dataKey="importance"
                radius={[0, 6, 6, 0]}
                >
                {topImportance.map(
                    (entry, index) => (
                    <Cell
                        key={entry.feature}
                    />
                    )
                )}
                </Bar>
            </BarChart>
            </ResponsiveContainer>
        </div>
        </div>

        <div className="panel insight-panel">
        <SectionTitle
            eyebrow="DATA SOURCES"
            title="Signals MIRAI Combines"
        />

        <div className="source-list">
            <div>
            <span className="source-number">01</span>
            <div>
                <strong>FRED</strong>
                <p>
                Macroeconomic and financial indicators
                including VIX, unemployment, CPI,
                industrial production, sentiment,
                housing and more.
                </p>
            </div>
            </div>

            <div>
            <span className="source-number">02</span>
            <div>
                <strong>EIA</strong>
                <p>
                Electricity and energy indicators
                representing activity and energy
                market pressure.
                </p>
            </div>
            </div>

            <div>
            <span className="source-number">03</span>
            <div>
                <strong>Behavioral Signals</strong>
                <p>
                Search-trend proxies for consumer
                caution, optimism, employment stress,
                financial anxiety and inflation fear.
                </p>
            </div>
            </div>
        </div>
        </div>
    </section>

    <section
        id="methodology"
        className="methodology"
    >
        <SectionTitle
        eyebrow="METHODOLOGY"
        title="From Raw Signals to Economic Forecast"
        />

        <div className="pipeline">
        <div className="pipeline-step">
            <span>01</span>
            <Database size={22} />
            <h3>Data Ingestion</h3>
            <p>
            Economic, energy and behavioral data
            are collected and standardized.
            </p>
        </div>

        <div className="pipeline-arrow">→</div>

        <div className="pipeline-step">
            <span>02</span>
            <Layers3 size={22} />
            <h3>Feature Engineering</h3>
            <p>
            Percentage changes, lags, rolling
            averages and rolling volatility are
            created from the time series.
            </p>
        </div>

        <div className="pipeline-arrow">→</div>

        <div className="pipeline-step">
            <span>03</span>
            <Gauge size={22} />
            <h3>ESS Construction</h3>
            <p>
            Rolling normalized indicators are
            combined into Macro, Energy and
            Behavioral stress components.
            </p>
        </div>

        <div className="pipeline-arrow">→</div>

        <div className="pipeline-step">
            <span>04</span>
            <BrainCircuit size={22} />
            <h3>ML Forecast</h3>
            <p>
            Historical features are used to predict
            the Economic Stress Score three months
            ahead.
            </p>
        </div>
        </div>
    </section>

    <section className="footer-note">
        <strong>MIRAI Research Disclaimer</strong>
        <p>
        The Economic Stress Score is a project-specific
        composite index, not an official government
        economic index. Model relationships are predictive,
        not causal, and historical performance does not
        guarantee future forecasting accuracy.
        </p>
    </section>
    </main>
</div>
);
}