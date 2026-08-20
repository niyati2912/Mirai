const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function request(path) {
const response = await fetch(`${API_BASE}${path}`);
if (!response.ok) {
throw new Error(`Request to ${path} failed with status ${response.status}`);
}
return response.json();
}

export function getDashboardData() {
return request("/api/dashboard");
}

export function getForecastData() {
return request("/api/forecast");
}

export function getModelAnalysis() {
return request("/api/model-analysis");
}

export function getMethodologyData() {
return request("/api/methodology");
}
