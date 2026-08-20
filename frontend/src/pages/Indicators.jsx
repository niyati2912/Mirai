import Panel from "../components/Panel";

function formatNumber(value) {
return Number.isFinite(Number(value))
? Number(value).toFixed(2)
: "—";
}

export default function Indicators({ data }) {
const { components } = data;

return (
<div className="page">
    <section className="page-intro">
    <div>
        <div className="eyebrow">
        SIGNAL UNIVERSE
        </div>

        <h1>Indicator Architecture</h1>

        <p>
        MIRAI combines conventional economic
        indicators with energy activity and
        behavioral search proxies.
        </p>
    </div>
    </section>

    <section className="indicator-grid">
    {components.map((component) => (
        <Panel
        key={component.id}
        title={component.name.toUpperCase()}
        subtitle={`ESS WEIGHT ${component.weight}%`}
        >
        <div className="indicator-card">
            <div className="indicator-score">
            {formatNumber(component.value)}
            </div>

            <p>
            {component.description}
            </p>

            <div className="indicator-weight">
            <span>CONTRIBUTION GROUP</span>

            <strong>
                {component.weight}%
            </strong>
            </div>
        </div>
        </Panel>
    ))}
    </section>
</div>
);
}