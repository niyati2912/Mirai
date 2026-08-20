import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, TrendingUp, BarChart3, Workflow, Plus, Database } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/forecast", label: "Forecast", icon: TrendingUp },
  { to: "/model-analysis", label: "Model Analysis", icon: BarChart3 },
  { to: "/methodology", label: "Methodology", icon: Workflow },
];

export default function Sidebar() {
  const navigate = useNavigate();

  // "New Analysis" re-runs a fresh fetch of dashboard data from the backend
  // rather than being a dead button — see Dashboard.jsx, which re-fetches
  // whenever it receives a new refreshToken via navigation state.
  function handleNewAnalysis() {
    navigate("/", { state: { refreshToken: Date.now() } });
  }

  return (
    <aside className="sidebar">
      <div>
        <div className="sidebar-group-label label-caps">Intelligence Unit</div>
        <div style={{ fontSize: 12, color: "var(--text-dim)", padding: "0 8px 12px" }}>
          Global Macro Desk
        </div>
        <button className="sidebar-new-analysis" onClick={handleNewAnalysis}>
          <Plus size={13} />
          New Analysis
        </button>
      </div>

      <nav style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `sidebar-item${isActive ? " active" : ""}`}
            style={({ isActive }) =>
              isActive ? { color: "var(--blue)", background: "var(--blue-tint)" } : undefined
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div style={{ marginTop: "auto", borderTop: "1px solid var(--border-strong)", paddingTop: 10 }}>
        <NavLink to="/methodology" className="sidebar-item">
          <Database size={14} />
          Data Sources
        </NavLink>
      </div>
    </aside>
  );
}
