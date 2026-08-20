export default function Panel({ title, controls, children, className = "" }) {
  return (
    <div className={`panel ${className}`}>
      {title && (
        <div className="panel-header">
          <span className="panel-title">{title}</span>
          {controls && <div className="panel-controls">{controls}</div>}
        </div>
      )}
      <div className="panel-body">{children}</div>
    </div>
  );
}
