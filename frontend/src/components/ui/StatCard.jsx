export default function StatCard({ icon: Icon, label, value, delta, tone = 'neutral' }) {
  const toneClass = {
    neutral: 'text-text-secondary',
    up: 'text-safe',
    down: 'text-malicious',
  }[tone];

  return (
    <div className="rounded-xl border border-border bg-surface p-5 shadow-card">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">
          {label}
        </span>
        {Icon && (
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface2 text-text-secondary">
            <Icon size={16} strokeWidth={2} />
          </span>
        )}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="font-display text-2xl font-semibold text-text-primary">{value}</span>
        {delta && <span className={`text-xs font-medium ${toneClass}`}>{delta}</span>}
      </div>
    </div>
  );
}