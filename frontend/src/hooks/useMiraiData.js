import { useEffect, useMemo, useState } from "react";
import Papa from "papaparse";

const DATA_PATH = "/data/";

function loadCSV(filename) {
return new Promise((resolve, reject) => {
Papa.parse(`${DATA_PATH}${filename}`, {
    download: true,
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    complete: (results) => {
    if (results.errors?.length) {
        console.warn(`${filename}:`, results.errors);
    }

    resolve(results.data || []);
    },
    error: reject,
});
});
}

function getNumeric(value) {
const number = Number(value);
return Number.isFinite(number) ? number : null;
}

function findColumn(row, candidates) {
if (!row) return null;

const keys = Object.keys(row);

for (const candidate of candidates) {
const exact = keys.find(
    (key) => key.toLowerCase() === candidate.toLowerCase()
);

if (exact) return exact;
}

for (const candidate of candidates) {
const partial = keys.find((key) =>
    key.toLowerCase().includes(candidate.toLowerCase())
);

if (partial) return partial;
}

return null;
}

function normaliseModelName(row) {
const possible = [
"Experiment",
"Model",
"model",
"experiment",
"Model_Name",
];

const column = findColumn(row, possible);

if (!column) return "Unknown Model";

return String(row[column] ?? "Unknown Model")
.replaceAll("_", " ")
.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function useMiraiData() {
const [essData, setEssData] = useState([]);
const [metrics, setMetrics] = useState([]);
const [predictions, setPredictions] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

useEffect(() => {
async function fetchData() {
    try {
    setLoading(true);

    const results = await Promise.allSettled([
        loadCSV("ess_dataset.csv"),
        loadCSV("model_metrics.csv"),
        loadCSV("model_predictions.csv"),
    ]);

    const [essResult, metricsResult, predictionsResult] = results;

    if (essResult.status !== "fulfilled") {
        throw new Error(
        "Could not load ess_dataset.csv from public/data."
        );
    }

    const sortedESS = essResult.value
        .filter((row) => row.Date)
        .sort(
        (a, b) =>
            new Date(a.Date).getTime() -
            new Date(b.Date).getTime()
        );

    setEssData(sortedESS);

    if (metricsResult.status === "fulfilled") {
        setMetrics(metricsResult.value.filter(Boolean));
    } else {
        console.warn(
        "model_metrics.csv could not be loaded"
        );
        setMetrics([]);
    }

    if (predictionsResult.status === "fulfilled") {
        const sortedPredictions =
        predictionsResult.value
            .filter(Boolean)
            .sort((a, b) => {
            const dateA =
                a.Date ||
                a.date ||
                a.Datetime ||
                "";

            const dateB =
                b.Date ||
                b.date ||
                b.Datetime ||
                "";

            return (
                new Date(dateA).getTime() -
                new Date(dateB).getTime()
            );
            });

        setPredictions(sortedPredictions);
    } else {
        console.warn(
        "model_predictions.csv could not be loaded"
        );
        setPredictions([]);
    }

    setError("");
    } catch (err) {
    console.error(err);

    setError(
        err.message ||
        "Unable to load MIRAI processed data."
    );
    } finally {
    setLoading(false);
    }
}

fetchData();
}, []);

const latest = useMemo(() => {
return essData.length
    ? essData[essData.length - 1]
    : null;
}, [essData]);

const previous = useMemo(() => {
return essData.length > 1
    ? essData[essData.length - 2]
    : null;
}, [essData]);

const ess = useMemo(() => {
return getNumeric(latest?.ESS);
}, [latest]);

const previousESS = useMemo(() => {
return getNumeric(previous?.ESS);
}, [previous]);

const essChange =
ess !== null && previousESS !== null
    ? ess - previousESS
    : null;

const components = useMemo(() => {
return [
    {
    id: "macro",
    name: "Macroeconomic",
    value: getNumeric(latest?.ESS_macro),
    weight: 45,
    description:
        "Traditional economic and financial indicators.",
    },
    {
    id: "energy",
    name: "Energy & Activity",
    value: getNumeric(latest?.ESS_energy),
    weight: 20,
    description:
        "Energy demand, generation and price pressure.",
    },
    {
    id: "behavioral",
    name: "Behavioral Signals",
    value: getNumeric(latest?.ESS_behavioral),
    weight: 35,
    description:
        "Search-based proxies for consumer concerns and expectations.",
    },
];
}, [latest]);

const chartData = useMemo(() => {
return essData
    .map((row) => ({
    date: row.Date,
    ESS: getNumeric(row.ESS),
    macro: getNumeric(row.ESS_macro),
    energy: getNumeric(row.ESS_energy),
    behavioral: getNumeric(row.ESS_behavioral),
    }))
    .filter((row) => row.ESS !== null);
}, [essData]);

const metricRows = useMemo(() => {
return metrics.map((row, index) => {
    const maeColumn = findColumn(row, ["MAE"]);
    const rmseColumn = findColumn(row, ["RMSE"]);
    const r2Column = findColumn(row, ["R2", "R²", "R_Squared"]);

    return {
    id: index,
    name: normaliseModelName(row),
    MAE: getNumeric(row[maeColumn]),
    RMSE: getNumeric(row[rmseColumn]),
    R2: getNumeric(row[r2Column]),
    raw: row,
    };
});
}, [metrics]);

const predictionInfo = useMemo(() => {
if (!predictions.length) {
    return {
    rows: [],
    dateColumn: null,
    actualColumn: null,
    modelColumns: [],
    };
}

const sample = predictions[0];

const dateColumn = findColumn(sample, [
    "Date",
    "date",
    "Datetime",
    "timestamp",
]);

const actualColumn = findColumn(sample, [
    "Actual",
    "Actual_ESS",
    "ESS_actual",
    "y_true",
    "Target",
]);

const excluded = new Set([
    dateColumn,
    actualColumn,
    "index",
    "Unnamed: 0",
]);

const modelColumns = Object.keys(sample).filter(
    (key) =>
    !excluded.has(key) &&
    predictions.some(
        (row) => getNumeric(row[key]) !== null
    )
);

const rows = predictions.map((row) => {
    const output = {
    date: dateColumn ? row[dateColumn] : null,
    actual: actualColumn
        ? getNumeric(row[actualColumn])
        : null,
    };

    modelColumns.forEach((column) => {
    output[column] = getNumeric(row[column]);
    });

    return output;
});

return {
    rows,
    dateColumn,
    actualColumn,
    modelColumns,
};
}, [predictions]);

return {
loading,
error,

essData,
metrics,
predictions,

latest,
previous,
ess,
previousESS,
essChange,

components,
chartData,
metricRows,
predictionInfo,
};
}