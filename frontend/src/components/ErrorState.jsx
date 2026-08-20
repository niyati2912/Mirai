export default function EmptyState({ message = "NO DATA AVAILABLE" }) {
  return (
    <div className="state-container">
      <span className="label-caps">{message}</span>
    </div>
  );
}
