export default function ErrorState({
  message = "Unable to load economic intelligence data.",
  onRetry,
}) {
  return (
    <div className="state-container">
      <span>{message}</span>
      {onRetry && (
        <button className="retry-btn" onClick={onRetry}>
          RETRY
        </button>
      )}
    </div>
  );
}
