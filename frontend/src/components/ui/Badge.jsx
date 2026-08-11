import { riskMeta } from '../../utils/risk';

export function RiskBadge({ level, size = 'md' }) {
  const meta = riskMeta(level);
  const padding = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium uppercase tracking-wide
        ${meta.bgClass} ${meta.colorClass} ${meta.borderClass} ${padding}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${meta.dotClass}`} />
      {meta.label}
    </span>
  );
}

export function Badge({ children, className = '' }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border border-border bg-surface2 px-2.5 py-1 text-xs text-text-secondary ${className}`}
    >
      {children}
    </span>
  );
}