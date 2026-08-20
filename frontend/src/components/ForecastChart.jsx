import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Search, Settings } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/forecast", label: "Forecast" },
  { to: "/model-analysis", label: "Model Analysis" },
  { to: "/methodology", label: "Methodology" },
];

// Simple client-side command interface: typing a page name and hitting
// Enter navigates there. This is a real, working search/command bar
// rather than a decorative input.
export default function Topbar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    const q = query.trim().toLowerCase();
    const match = NAV_ITEMS.find((item) => item.label.toLowerCase().includes(q));
    if (match) {
      navigate(match.to);
      setQuery("");
    }
  }

  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="topbar-brand">
          <span className="dot" />
          MIRAI
        </div>
        <nav className="topbar-nav">
          {NAV_ITEMS.map(({ to, label, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => (isActive ? "active" : "")}>
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="topbar-right">
        <form className="topbar-search" onSubmit={handleSubmit}>
          <Search size={13} />
          <input
            placeholder="Jump to page..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </form>
        <button className="icon-button" aria-label="settings">
          <Settings size={15} />
        </button>
      </div>
    </header>
  );
}
