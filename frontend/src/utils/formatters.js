export function formatNumber(value, decimals = 1) {
if (value === null || value === undefined || Number.isNaN(value)) return "—";
return Number(value).toFixed(decimals);
}

export function formatSigned(value, decimals = 1) {
if (value === null || value === undefined || Number.isNaN(value)) return "—";
const num = Number(value);
const sign = num > 0 ? "+" : "";
return `${sign}${num.toFixed(decimals)}`;
}

export function formatPercent(value, decimals = 1) {
if (value === null || value === undefined || Number.isNaN(value)) return "—";
return `${formatSigned(value, decimals)}%`;
}

export function formatDate(dateStr, options = { year: "numeric", month: "short" }) {
if (!dateStr) return "—";
const d = new Date(dateStr);
if (Number.isNaN(d.getTime())) return "—";
return d.toLocaleDateString("en-US", options);
}

export function stressStatus(ess) {
if (ess === null || ess === undefined || Number.isNaN(ess)) return null;
if (ess < 40) return "low";
if (ess < 65) return "moderate";
return "high";
}

export function filterByRange(history, range) {
if (!history || history.length === 0) return [];
if (range === "MAX") return history;
const months = range === "1Y" ? 12 : 60;
return history.slice(-months);
}
