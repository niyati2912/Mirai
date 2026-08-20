import { Database, Layers, GitBranch, Gauge, Target, TreePine, CheckCircle2 } from "lucide-react";

const STEPS = [
  { label: "Data Sources (FRED / EIA / Behavioral)", icon: Database },
  { label: "ETL Process", icon: Layers },
  { label: "Feature Engineering", icon: GitBranch },
  { label: "ESS Construction", icon: Gauge },
  { label: "3-Month Forecast Target", icon: Target },
  { label: "Random Forest Regression", icon: TreePine },
  { label: "Chronological Evaluation", icon: CheckCircle2 },
];

export default function PipelineDiagram() {
  return (
    <div className="pipeline-diagram">
      {STEPS.map((step, idx) => {
        const Icon = step.icon;
        return (
          <div key={step.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%" }}>
            <div className="pipeline-step">
              <span className="pipeline-step-icon">
                <Icon size={15} />
              </span>
              <span className="pipeline-step-label">{step.label}</span>
            </div>
            {idx < STEPS.length - 1 && <div className="pipeline-arrow">↓</div>}
          </div>
        );
      })}
    </div>
  );
}
