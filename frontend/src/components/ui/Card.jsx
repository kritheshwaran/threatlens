export default function Card({ className = '', children, ...props }) {
  return (
    <div
      className={`rounded-xl border border-border bg-surface shadow-card ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action, className = '' }) {
  return (
    <div className={`flex items-start justify-between gap-4 border-b border-border px-5 py-4 ${className}`}>
      <div>
        <h3 className="font-display text-sm font-semibold tracking-wide text-text-primary">
          {title}
        </h3>
        {subtitle && <p className="mt-0.5 text-xs text-text-secondary">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function CardBody({ className = '', children }) {
  return <div className={`px-5 py-4 ${className}`}>{children}</div>;
}