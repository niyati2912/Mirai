export default function Footer() {
  return (
    <footer className="app-footer">
      <span>MIRAI © {new Date().getFullYear()} — Economic Stress Intelligence</span>
      <span>
        <a href="https://fred.stlouisfed.org/" target="_blank" rel="noreferrer">
          FRED
        </a>
        <a href="https://www.eia.gov/" target="_blank" rel="noreferrer">
          EIA
        </a>
      </span>
    </footer>
  );
}
