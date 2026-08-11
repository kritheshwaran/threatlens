export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-border px-6 py-14 text-center">
      {Icon && (
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-surface2 text-text-secondary">
          <Icon size={20} strokeWidth={1.75} />
        </span>
      )}
      <div>
        <p className="font-display text-sm font-semibold text-text-primary">{title}</p>
        {description && <p className="mt-1 max-w-sm text-sm text-text-secondary">{description}</p>}
      </div>
      {action}
    </div>
  );
}