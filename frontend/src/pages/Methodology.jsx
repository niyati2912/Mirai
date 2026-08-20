import {
Activity,
BrainCircuit,
Database,
GitMerge,
Sigma,
TrendingUp,
} from "lucide-react";

import Panel from "../components/Panel";

const stages = [
{
number: "01",
title: "DATA SOURCES",
icon: Database,
text: "Traditional macroeconomic indicators, energy/activity data and behavioral search proxies are collected from external sources.",
detail: "FRED · EIA · Behavioral/Search Signals",
},
{
number: "02",
title: "ETL & ALIGNMENT",
icon: GitMerge,
text: "Source-specific datasets are transformed, dates are standardized and observations are merged into a unified time-series dataset.",
detail: "RAW → PROCESSED → MASTER DATASET",
},
{
number: "03",
title: "FEATURE ENGINEERING",
icon: Activity,
text: "Percentage changes, lagged observations, rolling means and rolling volatility features expand the information available to the forecasting model.",
detail: "PCT CHANGE · LAG1 · ROLLING 3 · ROLLING 6 · STD",
},
{
number: "04",
title: "ESS CONSTRUCTION",
icon: Sigma,
text: "Indicators are converted into directionally consistent rolling Z-scores and aggregated into Macro, Energy and Behavioral components.",
detail: "45% MACRO · 20% ENERGY · 35% BEHAVIORAL",
},
{
number: "05",
title: "RANDOM FOREST",
icon: BrainCircuit,
text: "Current and historical features are used to predict the future Economic Stress Score using Random Forest regression.",
detail: "X → CURRENT/HISTORICAL FEATURES · y → ESS + 3",
},
{
number: "06",
title: "CHRONOLOGICAL EVALUATION",
icon: TrendingUp,
text: "Older observations are used for training and newer observations for testing to respect the temporal structure of economic forecasting.",
detail: "TRAIN PAST → TEST FUTURE",
},
];

export default function Methodology() {
return (
<div className="page methodology-page">
    <section className="page-intro">
    <div>
        <div className="eyebrow">
        SYSTEM DESIGN
        </div>

        <h1>How MIRAI Works</h1>

        <p>
        From raw economic signals to a
        project-specific Economic Stress Score
        and three-month forecasting target.
        </p>
    </div>
    </section>

    <Panel
    title="MIRAI INTELLIGENCE PIPELINE"
    subtitle="End-to-end architecture"
    >
    <div className="methodology-pipeline">
        {stages.map((stage, index) => {
        const Icon = stage.icon;

        return (
            <div
            className="method-stage"
            key={stage.number}
            >
            <div className="method-stage-top">
                <span>{stage.number}</span>

                <Icon size={20} />
            </div>

            <h3>{stage.title}</h3>

            <p>{stage.text}</p>

            <code>{stage.detail}</code>

            {index <
                stages.length - 1 && (
                <div className="method-connector">
                ↓
                </div>
            )}
            </div>
        );
        })}
    </div>
    </Panel>

    <section className="methodology-detail-grid">
    <Panel title="ECONOMIC STRESS SCORE">
        <div className="method-detail">
        <div className="formula">
            ESS = 0.45 × Macro
            <br />
            + 0.20 × Energy
            <br />
            + 0.35 × Behavioral
        </div>

        <p>
            Each category is built from
            directionally aligned normalized
            indicators. Higher final values
            represent greater project-defined
            economic stress.
        </p>

        <span>
            PROJECT-SPECIFIC INDEX · NOT AN
            OFFICIAL GOVERNMENT MEASURE
        </span>
        </div>
    </Panel>

    <Panel title="FORECAST TARGET">
        <div className="method-detail">
        <div className="formula">
            ESS_target = ESS.shift(-3)
        </div>

        <p>
            The model is not designed to predict
            the current ESS. Features available
            at one point in time are mapped to
            the Economic Stress Score three
            months later.
        </p>

        <span>
            JANUARY FEATURES → APRIL ESS
        </span>
        </div>
    </Panel>

    <Panel title="RESEARCH LIMITATIONS">
        <div className="limitations-list">
        <div>
            <span>01</span>
            ESS is a constructed project index.
        </div>

        <div>
            <span>02</span>
            Category weights are design choices,
            not causal weights.
        </div>

        <div>
            <span>03</span>
            Behavioral search signals are proxies,
            not direct economic measurements.
        </div>

        <div>
            <span>04</span>
            Predictive relationships do not imply
            causality.
        </div>

        <div>
            <span>05</span>
            Historical model performance does not
            guarantee future forecasting success.
        </div>
        </div>
    </Panel>
    </section>
</div>
);
}