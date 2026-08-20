const API = "http://127.0.0.1:8000";

let state = {
dashboard: null,
metrics: null,
predictions: null,
indicators: null,
currentPage: "dashboard",
chart: null,
};

document.addEventListener("DOMContentLoaded", async () => {
document.getElementById("currentDate").textContent =
new Date().toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
});

setupNavigation();
await loadData();
renderPage();
});

function setupNavigation() {
document.querySelectorAll(".nav-item").forEach((button) => {
button.addEventListener("click", () => {
    state.currentPage = button.dataset.page;

    document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.remove("active");
    });

    button.classList.add("active");

    renderPage();
});
});
}

async function fetchAPI(endpoint) {
const response = await fetch(`${API}${endpoint}`);

if (!response.ok) {
throw new Error(
    `API ${response.status}: ${response.statusText}`
);
}

return response.json();
}

async function loadData() {
try {
const [
    dashboard,
    metrics,
    predictions,
    indicators,
] = await Promise.all([
    fetchAPI("/api/dashboard"),
    fetchAPI("/api/model-metrics"),
    fetchAPI("/api/model-predictions"),
    fetchAPI("/api/feature-importance"),
]);

state.dashboard = dashboard;
state.metrics = metrics;
state.predictions = predictions;
state.indicators = indicators;
} catch (error) {
console.error(error);

document.getElementById("appContent").innerHTML = `
    <div class="center-state">
    <h2>DATA CONNECTION FAILED</h2>
    <p>
        MIRAI could not retrieve the project data
        from the FastAPI backend.
    </p>

    <button
        class="retry-button"
        onclick="location.reload()"
    >
        RETRY CONNECTION
    </button>
    </div>
`;
}
}

function renderPage() {
if (!state.dashboard) return;

const content = document.getElementById("appContent");

if (state.currentPage === "dashboard") {
content.innerHTML = dashboardPage();
drawESSChart();
return;
}

if (state.currentPage === "indicators") {
content.innerHTML = indicatorsPage();
return;
}

if (state.currentPage === "forecast") {
content.innerHTML = forecastPage();
drawForecastChart();
return;
}

if (state.currentPage === "models") {
content.innerHTML = modelsPage();
return;
}

if (state.currentPage === "methodology") {
content.innerHTML = methodologyPage();
}
}

/* -------------------------------------------------------
DATA HELPERS
------------------------------------------------------- */

function getESSRows() {
return state.dashboard?.ess || [];
}

function getLatestESS() {
const rows = getESSRows();

if (!rows.length) return null;

return rows[rows.length - 1];
}

function numeric(value) {
const number = Number(value);

return Number.isFinite(number)
? number
: null;
}

function formatNumber(value, decimals = 1) {
const number = numeric(value);

return number === null
? "—"
: number.toFixed(decimals);
}

function formatDate(value) {
if (!value) return "—";

const date = new Date(value);

if (Number.isNaN(date.getTime())) {
return String(value);
}

return date.toLocaleDateString("en-US", {
month: "short",
year: "numeric",
});
}

function stressStatus(score) {
const value = numeric(score);

if (value === null) {
return {
    label: "UNAVAILABLE",
    className: "status-medium",
};
}

if (value >= 70) {
return {
    label: "HIGH STRESS",
    className: "status-high",
};
}

if (value >= 40) {
return {
    label: "MODERATE",
    className: "status-medium",
};
}

return {
label: "LOW STRESS",
className: "status-low",
};
}

function getComponents() {
const latest = getLatestESS();

if (!latest) return [];

return [
{
    name: "MACRO",
    weight: 45,
    value: numeric(latest.ESS_macro),
    description:
    "Traditional economic and financial indicators.",
},
{
    name: "ENERGY",
    weight: 20,
    value: numeric(latest.ESS_energy),
    description:
    "Energy activity and cost-pressure signals.",
},
{
    name: "BEHAVIORAL",
    weight: 35,
    value: numeric(latest.ESS_behavioral),
    description:
    "Search-based proxies for economic anxiety and expectations.",
},
];
}

function getBestModel() {
const rows =
state.metrics?.metrics || [];

const usable = rows.filter(
(row) => numeric(row.RMSE) !== null
);

return usable.sort(
(a, b) =>
    numeric(a.RMSE) -
    numeric(b.RMSE)
)[0];
}

/* -------------------------------------------------------
DASHBOARD
------------------------------------------------------- */

function dashboardPage() {
const latest = getLatestESS();

const ess = numeric(latest?.ESS);

const rows = getESSRows();

const previous =
rows.length > 1
    ? numeric(rows[rows.length - 2]?.ESS)
    : null;

const change =
ess !== null && previous !== null
    ? ess - previous
    : null;

const status = stressStatus(ess);
const bestModel = getBestModel();
const components = getComponents();

return `
<div class="page">

    <div class="page-header">
    <div>
        <div class="eyebrow">
        LIVE ECONOMIC INTELLIGENCE
        </div>

        <h1 class="page-title">
        Economic Stress Monitor
        </h1>

        <p class="page-description">
        Mirai combines macroeconomic, energy and
        behavioral signals into a project-specific
        Economic Stress Score and forecasts future
        economic stress.
        </p>
    </div>

    <div>
        <div class="status-badge ${status.className}">
        ${status.label}
        </div>

        <div
        style="
            color: var(--muted-2);
            font-family: 'JetBrains Mono';
            font-size: 8px;
            margin-top: 9px;
            text-align: right;
        "
        >
        LATEST · ${formatDate(latest?.Date)}
        </div>
    </div>
    </div>

    <section class="metric-grid">

    ${metricCard(
        "CURRENT ESS",
        formatNumber(ess),
        "/100",
        status.label,
        "PROJECT COMPOSITE"
    )}

    ${metricCard(
        "MONTHLY MOVEMENT",
        change === null
        ? "—"
        : `${change >= 0 ? "+" : ""}${formatNumber(change)}`,
        "",
        change === null
        ? "NO COMPARISON"
        : change > 0
        ? "STRESS RISING"
        : "STRESS EASING",
        "VERSUS PRIOR OBSERVATION"
    )}

    ${metricCard(
        "FORECAST HORIZON",
        "3",
        "MONTHS",
        "FORWARD LOOKING",
        "ESS TARGET SHIFT"
    )}

    ${metricCard(
        "BEST RMSE",
        bestModel
        ? formatNumber(bestModel.RMSE, 2)
        : "—",
        "",
        "MODEL PERFORMANCE",
        bestModel?.Model ||
        bestModel?.model ||
        "PROCESSED OUTPUT"
    )}

    </section>

    <section class="grid-two">

    <div class="panel chart-panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            ECONOMIC STRESS SCORE
            </div>

            <div class="panel-subtitle">
            Historical composite index
            </div>
        </div>

        <div class="range-controls">
            <button class="active" onclick="changeChartRange(60)">
            5Y
            </button>

            <button onclick="changeChartRange(120)">
            10Y
            </button>

            <button onclick="changeChartRange(null)">
            MAX
            </button>
        </div>
        </div>

        <div class="chart-container">
        <canvas id="essChart"></canvas>
        </div>

        <div class="chart-footer">
        <span>
            PROJECT-SPECIFIC INDEX
        </span>

        <span>
            MACRO 45% · ENERGY 20% · BEHAVIORAL 35%
        </span>
        </div>
    </div>

    <div class="panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            SIGNAL ARCHITECTURE
            </div>

            <div class="panel-subtitle">
            Latest category-level stress
            </div>
        </div>
        </div>

        <div class="panel-body">
        <div class="signal-list">

            ${components
            .map(
                (component) => `
                <div>
                    <div class="signal-header">

                    <div>
                        <div class="signal-name">
                        ${component.name}
                        </div>

                        <div class="signal-weight">
                        WEIGHT ${component.weight}%
                        </div>
                    </div>

                    <div class="signal-score">
                        ${formatNumber(
                        component.value,
                        2
                        )}
                    </div>
                    </div>

                    <div class="signal-track">
                    <div
                        class="signal-fill"
                        style="
                        width: ${Math.max(
                            3,
                            Math.min(
                            100,
                            ((component.value + 3) / 6) * 100
                            )
                        )}%;
                        "
                    ></div>
                    </div>

                    <div class="signal-description">
                    ${component.description}
                    </div>
                </div>
                `
            )
            .join("")}

        </div>
        </div>
    </div>

    </section>

    <section class="grid-equal">

    <div class="panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            INTELLIGENCE SUMMARY
            </div>

            <div class="panel-subtitle">
            What the latest observation says
            </div>
        </div>
        </div>

        <div class="panel-body">
        <div class="intelligence-list">

            <div class="intelligence-card">
            <div class="intelligence-icon">
                ◈
            </div>

            <div class="intelligence-title">
                STRESS REGIME
            </div>

            <div class="intelligence-value">
                ${status.label}
            </div>

            <div class="intelligence-text">
                Current ESS is
                ${formatNumber(ess)}
                on Mirai's normalized 0–100
                project scale.
            </div>
            </div>

            <div class="intelligence-card">
            <div class="intelligence-icon">
                ${change > 0 ? "↗" : "↘"}
            </div>

            <div class="intelligence-title">
                RECENT DIRECTION
            </div>

            <div class="intelligence-value">
                ${
                change === null
                    ? "UNAVAILABLE"
                    : change > 0
                    ? "STRESS INCREASING"
                    : "STRESS DECREASING"
                }
            </div>

            <div class="intelligence-text">
                Change from the previous
                observation:
                ${
                change === null
                    ? "—"
                    : `${change >= 0 ? "+" : ""}${formatNumber(
                        change
                    )}`
                }.
            </div>
            </div>

            <div class="intelligence-card">
            <div class="intelligence-icon">
                Σ
            </div>

            <div class="intelligence-title">
                COMPOSITE DESIGN
            </div>

            <div class="intelligence-value">
                45 / 20 / 35
            </div>

            <div class="intelligence-text">
                Macro, energy and behavioral
                components are combined using
                the project's fixed weights.
            </div>
            </div>

        </div>
        </div>
    </div>

    <div class="panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            SYSTEM PIPELINE
            </div>

            <div class="panel-subtitle">
            From raw signal to forecast
            </div>
        </div>
        </div>

        <div class="panel-body">
        <div class="pipeline">

            <div class="pipeline-node">
            <span>01</span>
            <strong>DATA</strong>
            </div>

            <div class="pipeline-line"></div>

            <div class="pipeline-node">
            <span>02</span>
            <strong>FEATURES</strong>
            </div>

            <div class="pipeline-line"></div>

            <div class="pipeline-node">
            <span>03</span>
            <strong>ESS</strong>
            </div>

            <div class="pipeline-line"></div>

            <div class="pipeline-node">
            <span>04</span>
            <strong>3M MODEL</strong>
            </div>

        </div>

        <div class="intelligence-text">
            External indicators → engineered
            features → normalized Economic Stress
            Score → future ESS prediction.
        </div>
        </div>
    </div>

    </section>

</div>
`;
}

function metricCard(
label,
value,
suffix,
status,
note
) {
return `
<div class="metric-card">

    <div class="metric-label">
    ${label}
    </div>

    <div class="metric-value">
    ${value}

    ${
        suffix
        ? `<small>${suffix}</small>`
        : ""
    }
    </div>

    <div class="metric-status">
    ${status}
    </div>

    <div class="metric-note">
    ${note}
    </div>

</div>
`;
}

/* -------------------------------------------------------
ESS CHART
------------------------------------------------------- */

function drawESSChart(limit = 60) {
const canvas =
document.getElementById("essChart");

if (!canvas) return;

const rows = getESSRows();

const selected =
limit === null
    ? rows
    : rows.slice(-limit);

if (state.chart) {
state.chart.destroy();
}

state.chart = new Chart(canvas, {
type: "line",

data: {
    labels: selected.map(
    (row) => formatDate(row.Date)
    ),

    datasets: [
    {
        data: selected.map(
        (row) => numeric(row.ESS)
        ),

        borderColor: "#86d7ff",
        backgroundColor:
        "rgba(134,215,255,0.07)",

        borderWidth: 1.8,
        pointRadius: 0,
        pointHoverRadius: 4,

        fill: true,
        tension: 0.25,
    },
    ],
},

options: {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
    legend: {
        display: false,
    },

    tooltip: {
        backgroundColor: "#111a22",
        borderColor: "#283540",
        borderWidth: 1,

        titleColor: "#7d8994",
        bodyColor: "#edf3f7",

        displayColors: false,

        callbacks: {
        label: (context) =>
            ` ESS: ${Number(
            context.raw
            ).toFixed(2)}`,
        },
    },
    },

    scales: {
    x: {
        grid: {
        display: false,
        },

        ticks: {
        color: "#53606c",
        font: {
            family: "JetBrains Mono",
            size: 8,
        },

        maxTicksLimit: 8,
        },

        border: {
        display: false,
        },
    },

    y: {
        grid: {
        color: "#1b252e",
        },

        ticks: {
        color: "#53606c",
        font: {
            family: "JetBrains Mono",
            size: 8,
        },
        },

        border: {
        display: false,
        },
    },
    },
},
);
}

function changeChartRange(limit) {
drawESSChart(limit);
}

/* -------------------------------------------------------
INDICATORS
------------------------------------------------------- */

function indicatorsPage() {
const rows =
state.dashboard?.ess || [];

const latest =
rows[rows.length - 1] || {};

const groups = [
{
    title: "MACROECONOMIC",
    weight: "45%",
    items: [
    "VIX",
    "Yield Curve",
    "Unemployment Rate",
    "CPI",
    "Federal Funds Rate",
    "Industrial Production",
    "Consumer Sentiment",
    "Housing Starts",
    "Retail Sales",
    "Building Permits",
    ],
},

{
    title: "ENERGY",
    weight: "20%",
    items: [
    "Electricity Demand",
    "Electricity Generation",
    "Natural Gas Prices",
    "Petroleum Prices",
    ],
},

{
    title: "BEHAVIORAL",
    weight: "35%",
    items: [
    "Consumer Caution",
    "Economic Optimism",
    "Employment Stress",
    "Financial Anxiety",
    "Housing Stress",
    "Inflation Fear",
    ],
},
];

return `
<div class="page">

    <div class="page-header">
    <div>
        <div class="eyebrow">
        SIGNAL INTELLIGENCE
        </div>

        <h1 class="page-title">
        Economic Indicators
        </h1>

        <p class="page-description">
        Mirai combines conventional economic
        measures with energy and behavioral
        signals to construct its composite
        stress index.
        </p>
    </div>
    </div>

    <section class="grid-two">

    ${groups
        .map(
        (group) => `
            <div class="panel">

            <div class="panel-header">
                <div>
                <div class="panel-title">
                    ${group.title}
                </div>

                <div class="panel-subtitle">
                    Signals contributing to ESS
                </div>
                </div>

                <div class="status-badge status-low">
                ${group.weight}
                </div>
            </div>

            <div class="panel-body">

                <table class="data-table">

                <thead>
                    <tr>
                    <th>INDICATOR</th>
                    <th>ROLE</th>
                    </tr>
                </thead>

                <tbody>

                    ${group.items
                    .map(
                        (item) => `
                        <tr>
                            <td>
                            ${item}
                            </td>

                            <td>
                            PROJECT SIGNAL
                            </td>
                        </tr>
                        `
                    )
                    .join("")}

                </tbody>

                </table>

            </div>
            </div>
        `
        )
        .join("")}

    </section>

    <div class="panel">
    <div class="panel-header">
        <div>
        <div class="panel-title">
            LATEST COMPONENT OUTPUT
        </div>

        <div class="panel-subtitle">
            Actual values produced by the ESS pipeline
        </div>
        </div>
    </div>

    <div class="panel-body">

        <table class="data-table">

        <thead>
            <tr>
            <th>COMPONENT</th>
            <th>VALUE</th>
            <th>WEIGHT</th>
            </tr>
        </thead>

        <tbody>

            <tr>
            <td>ESS Macro</td>
            <td>${formatNumber(
                latest.ESS_macro,
                3
            )}</td>
            <td>45%</td>
            </tr>

            <tr>
            <td>ESS Energy</td>
            <td>${formatNumber(
                latest.ESS_energy,
                3
            )}</td>
            <td>20%</td>
            </tr>

            <tr>
            <td>ESS Behavioral</td>
            <td>${formatNumber(
                latest.ESS_behavioral,
                3
            )}</td>
            <td>35%</td>
            </tr>

            <tr>
            <td>Economic Stress Score</td>
            <td>${formatNumber(
                latest.ESS,
                3
            )}</td>
            <td>COMPOSITE</td>
            </tr>

        </tbody>

        </table>

    </div>
    </div>

</div>
`;
}

/* -------------------------------------------------------
FORECAST
------------------------------------------------------- */

function forecastPage() {
const predictions =
state.predictions?.data ||
state.predictions?.predictions ||
[];

const latest = predictions[
predictions.length - 1
];

const forecastValue =
numeric(
    latest?.Predicted_ESS
) ??
numeric(
    latest?.predicted
) ??
numeric(
    latest?.prediction
);

const status =
stressStatus(forecastValue);

return `
<div class="page">

    <div class="page-header">
    <div>
        <div class="eyebrow">
        FORWARD ECONOMIC INTELLIGENCE
        </div>

        <h1 class="page-title">
        3-Month Stress Forecast
        </h1>

        <p class="page-description">
        Mirai uses current and historical
        engineered economic features to predict
        future Economic Stress Score.
        </p>
    </div>

    <div class="status-badge ${status.className}">
        ${status.label}
    </div>
    </div>

    <section class="forecast-hero">

    <div class="forecast-box">

        <div class="forecast-label">
        LATEST MODEL FORECAST
        </div>

        <div class="forecast-number">
        ${formatNumber(
            forecastValue,
            2
        )}

        <small>/100</small>
        </div>

        <div class="forecast-description">
        Predicted future Economic Stress Score
        from the project's model output.
        </div>

    </div>

    <div class="forecast-box">

        <div class="forecast-label">
        FORECAST DESIGN
        </div>

        <div class="forecast-number">
        +3
        <small>MONTHS</small>
        </div>

        <div class="forecast-description">
        The target is created by shifting ESS
        three periods into the future.
        </div>

    </div>

    </section>

    <div class="panel" style="margin-top:14px">

    <div class="panel-header">
        <div>
        <div class="panel-title">
            ACTUAL VS PREDICTED ESS
        </div>

        <div class="panel-subtitle">
            Model predictions from the generated output
        </div>
        </div>
    </div>

    <div class="chart-container">
        <canvas id="forecastChart"></canvas>
    </div>

    </div>

</div>
`;
}

function drawForecastChart() {
const canvas =
document.getElementById(
    "forecastChart"
);

if (!canvas) return;

const predictions =
state.predictions?.data ||
state.predictions?.predictions ||
[];

const labels = predictions.map(
(row) =>
    formatDate(
    row.Date ||
    row.date
    )
);

const actual = predictions.map(
(row) =>
    numeric(
    row.Actual_ESS
    ) ??
    numeric(row.actual) ??
    numeric(row.ESS)
);

const predicted = predictions.map(
(row) =>
    numeric(
    row.Predicted_ESS
    ) ??
    numeric(row.predicted) ??
    numeric(row.prediction)
);

new Chart(canvas, {
type: "line",

data: {
    labels,

    datasets: [
    {
        label: "Actual ESS",
        data: actual,
        borderColor: "#edf3f7",
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0.2,
    },

    {
        label: "Predicted ESS",
        data: predicted,
        borderColor: "#86d7ff",
        borderWidth: 1.8,
        pointRadius: 0,
        tension: 0.2,
    },
    ],
},

options: {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
    legend: {
        labels: {
        color: "#7d8994",
        font: {
            family: "JetBrains Mono",
            size: 9,
        },
        },
    },
    },

    scales: {
    x: {
        ticks: {
        color: "#53606c",
        maxTicksLimit: 8,
        },
        grid: {
        display: false,
        },
    },

    y: {
        ticks: {
        color: "#53606c",
        },
        grid: {
        color: "#1b252e",
        },
    },
    },
},
});
}

/* -------------------------------------------------------
MODEL ANALYSIS
------------------------------------------------------- */

function modelsPage() {
const rows =
state.metrics?.metrics || [];

const sorted = [...rows].sort(
(a, b) =>
    numeric(a.RMSE) -
    numeric(b.RMSE)
);

return `
<div class="page">

    <div class="page-header">
    <div>
        <div class="eyebrow">
        MODEL EVALUATION
        </div>

        <h1 class="page-title">
        Model Analysis
        </h1>

        <p class="page-description">
        Evaluating forecasting performance and
        testing whether behavioral signals add
        predictive value.
        </p>
    </div>
    </div>

    <div class="panel">

    <div class="panel-header">
        <div>
        <div class="panel-title">
            MODEL COMPARISON
        </div>

        <div class="panel-subtitle">
            Lower MAE/RMSE is better · higher R² is better
        </div>
        </div>
    </div>

    <div class="panel-body">

        <table class="data-table">

        <thead>
            <tr>
            <th>MODEL</th>
            <th>MAE</th>
            <th>RMSE</th>
            <th>R²</th>
            </tr>
        </thead>

        <tbody>

            ${
            sorted.length
                ? sorted
                    .map(
                    (row, index) => `
                        <tr>
                        <td>
                            ${
                            index === 0
                                ? "★ "
                                : ""
                            }

                            ${
                            row.Model ||
                            row.model ||
                            row.name ||
                            `Model ${index + 1}`
                            }
                        </td>

                        <td>
                            ${formatNumber(
                            row.MAE,
                            3
                            )}
                        </td>

                        <td>
                            ${formatNumber(
                            row.RMSE,
                            3
                            )}
                        </td>

                        <td>
                            ${formatNumber(
                            row["R²"] ??
                                row.R2,
                            3
                            )}
                        </td>
                        </tr>
                    `
                    )
                    .join("")
                : `
                <tr>
                    <td colspan="4">
                    No model metrics available.
                    </td>
                </tr>
                `
            }

        </tbody>

        </table>

    </div>
    </div>

    <section
    class="grid-two"
    style="margin-top:14px"
    >

    <div class="panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            THE HYPOTHESIS
            </div>

            <div class="panel-subtitle">
            What Mirai is testing
            </div>
        </div>
        </div>

        <div class="panel-body">

        <div class="forecast-number">
            + BEHAVIOR
        </div>

        <p class="forecast-description">
            Can unconventional behavioral/search
            signals provide useful additional
            information beyond conventional
            economic indicators?
        </p>

        </div>
    </div>

    <div class="panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            INTERPRETATION
            </div>

            <div class="panel-subtitle">
            What the metrics actually tell us
            </div>
        </div>
        </div>

        <div class="panel-body">

        <p class="forecast-description">
            MAE measures average absolute error.
            RMSE penalizes larger errors more
            heavily. R² measures explained
            variation relative to a baseline.
        </p>

        <p class="forecast-description">
            These metrics evaluate predictive
            performance; they do not establish
            causal relationships.
        </p>

        </div>
    </div>

    </section>

</div>
`;
}

/* -------------------------------------------------------
METHODOLOGY
------------------------------------------------------- */

function methodologyPage() {
const steps = [
[
    "01",
    "DATA INGESTION",
    "FRED, EIA and behavioral/search signals are collected and standardized into time-series datasets.",
    ["FRED", "EIA", "BEHAVIORAL"],
],

[
    "02",
    "FEATURE ENGINEERING",
    "Each numeric indicator is transformed using percentage change, lagged values, rolling means and rolling volatility.",
    ["PCT CHANGE", "LAG 1", "ROLLING 3", "ROLLING 6", "STD"],
],

[
    "03",
    "ESS CONSTRUCTION",
    "Rolling Z-scores normalize indicators and align their direction so higher values consistently represent greater stress.",
    ["12-MONTH WINDOW", "45 / 20 / 35", "0–100"],
],

[
    "04",
    "RANDOM FOREST",
    "A Random Forest regression model learns nonlinear relationships between engineered features and future ESS.",
    ["REGRESSION", "ENSEMBLE", "NONLINEAR"],
],

[
    "05",
    "FORECAST",
    "ESS is shifted three periods forward, turning the problem into a future economic-stress forecasting task.",
    ["3-MONTH HORIZON"],
],
];

return `
<div class="page">

    <div class="page-header">
    <div>
        <div class="eyebrow">
        MIRAI RESEARCH PIPELINE
        </div>

        <h1 class="page-title">
        From Signals to Forecasts
        </h1>

        <p class="page-description">
        The complete transformation from external
        observations to Mirai's future Economic
        Stress Score.
        </p>
    </div>
    </div>

    <div class="methodology">

    ${steps
        .map(
        (step) => `
            <div class="method-step">

            <div class="method-number">
                ${step[0]}
            </div>

            <div class="method-icon">
                Σ
            </div>

            <div>

                <div class="method-title">
                ${step[1]}
                </div>

                <div class="method-description">
                ${step[2]}
                </div>

                <div class="method-tags">

                ${step[3]
                    .map(
                    (tag) => `
                        <span class="method-tag">
                        ${tag}
                        </span>
                    `
                    )
                    .join("")}

                </div>

            </div>

            </div>
        `
        )
        .join("")}

    </div>

    <section
    class="grid-two"
    style="margin-top:14px"
    >

    <div class="panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            ESS DESIGN
            </div>

            <div class="panel-subtitle">
            Project-specific composite index
            </div>
        </div>
        </div>

        <div class="panel-body">

        <div class="metric-value">
            45 / 20 / 35
        </div>

        <p class="forecast-description">
            Macro receives 45%, energy 20% and
            behavioral signals 35%. These are
            design choices for the project, not
            learned causal weights.
        </p>

        </div>
    </div>

    <div class="panel">
        <div class="panel-header">
        <div>
            <div class="panel-title">
            LIMITATIONS
            </div>

            <div class="panel-subtitle">
            What Mirai does not claim
            </div>
        </div>
        </div>

        <div class="panel-body">

        <p class="forecast-description">
            ESS is not an official government
            economic index.
        </p>

        <p class="forecast-description">
            Behavioral search data is a proxy,
            not direct measurement of economic
            conditions.
        </p>

        <p class="forecast-description">
            Random Forest identifies predictive
            relationships, not causality.
        </p>

        </div>
    </div>

    </section>

</div>
`;
}