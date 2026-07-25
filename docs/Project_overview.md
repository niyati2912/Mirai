# Economic Early Warning System — Project Overview

## Problem Statement
Predict early signs of economic stress or growth in specific sectors by tracking unconventional real-world signals — search trends, fuel prices, grocery costs, layoffs — before official indicators like GDP or unemployment data confirm it.

## Core Idea
Most prediction models run on standard financial/economic data that everyone already uses. This system is differentiated because it ingests signals nobody systematically models together — behavioral and everyday signals (search behavior, fuel prices, grocery costs, layoffs) — treating the real world's everyday texture as the predictive input, not an afterthought.

The theoretical grounding is **behavioral economics**: people's search behavior, spending shifts, and small purchase choices change based on psychology and sentiment before hard economic numbers (GDP, unemployment) catch up and confirm it. A **recession** is the thing being detected early — a significant, widespread decline in economic activity, officially flagged by NBER (`USREC` series).

## What It Outputs
A sector-status dashboard. Each sector gets a classified status label, e.g.:

| Sector | Example Status |
|---|---|
| Retail | Healthy |
| Manufacturing | Moderate stress |
| Hospitality | High growth |
| Agriculture | Weather risk |

Each label is paired with a plain-language explanation of *why* (which indicators drove it), so it's useful for businesses, policymakers, or investors — not just a black-box number.

## Architecture (4 layers)
```
[Data Collection] → [Feature Store] → [ML Classification Model] → [FastAPI Backend] → [React Dashboard]
                                                  ↑
                                    [LLM Explanation Layer]
```
1. **Data collection** — pulls/updates alternative indicator data
2. **Feature store** — structured time-series data (pandas → CSV for now, DB later)
3. **ML layer** — classifies each sector's status
4. **App layer** — React dashboard + LLM explains the "why"

## Tech Stack

**Data collection**
- `fredapi` — inflation, unemployment, fuel prices, jobless claims, food/grocery CPI
- `pytrends` — Google Trends search volume (behavioral signals)
- `yfinance` — sector ETF prices, used as ground truth for labeling sector performance
- `python-dotenv` — keep API keys out of code

**Storage**
- pandas DataFrame → CSV for now. Add SQLite/Postgres only once automating scheduled updates.

**ML**
- `scikit-learn` — start with Logistic Regression (interpretable, gives feature weights), then Random Forest (handles nonlinear relationships, gives `feature_importances_`)
- Only move to XGBoost/LightGBM once there's enough historical data (100+ time periods) — avoid deep learning, not enough data and it hurts explainability
- `pandas` + `numpy` — feature engineering (rolling averages, % change, lag features)

**Explanation layer**
- Anthropic/OpenAI API — single prompt call: feed feature values + predicted label, get plain-language explanation. No agent framework needed yet.

**Backend**
- FastAPI — serves predictions + explanations as JSON to the frontend

**Frontend**
- React — sector cards, color-coded by status, expandable to show driving indicators + explanation

## Data Plan

| Signal | Source | Series/Query |
|---|---|---|
| Inflation | FRED | `CPIAUCSL` |
| Unemployment | FRED | `UNRATE` |
| Layoffs/jobless claims | FRED | `ICSA` |
| Fuel prices | FRED | `GASREGW` |
| Grocery/food prices | FRED | `CPIUFDSL` |
| Recession (training label) | FRED | `USREC` (NBER's official recession flag, monthly, binary) |
| Job search behavior | pytrends | "unemployment benefits", "job search" |
| Bankruptcy sentiment | pytrends | "bankruptcy", "file for bankruptcy" |
| Sector performance (target) | yfinance | Sector ETFs: XLY, XLP, XLI, XLE, XLF |

## Build Order / Roadmap

**Phase 1 — Prove the concept, one sector, static data**
- Pull `CPIAUCSL`, `UNRATE`, `ICSA`, `GASREGW`, `USREC` from FRED, merge into one DataFrame by month
- Add pytrends search volume for 2-3 keywords
- Train Logistic Regression: features = indicators, label = `USREC`
- Check accuracy, inspect which features had the most weight

**Phase 2 — Add automation for one sector**
- Automate data pulling (scheduled script)
- Add LLM explanation step
- Wire through FastAPI to React (not hardcoded)

**Phase 3 — Expand to 3-4 sectors**
- Move from a single national recession label to sector-specific labels (using yfinance sector ETF returns instead of just `USREC`)
- Add Retail, Manufacturing, Hospitality, Agriculture one at a time

**Phase 4 — Polish**
- Unsupervised clustering (KMeans/PCA) to find indicator correlations not yet named — the "discovery" angle
- Historical backtesting — show the model would've flagged stress before it hit the news
- Dashboard polish, confidence scores per prediction

## Key Design Decisions Already Made
- Output type: **multi-class classification** (status labels), not regression
- Training label source: **`USREC`** (NBER official recession indicator) for the first working version
- Start simple: **Logistic Regression → Random Forest → XGBoost**, in that order, only upgrading once the simpler model works
- Don't build the agent layer first — validate the ML core on manually-pulled data before automating collection