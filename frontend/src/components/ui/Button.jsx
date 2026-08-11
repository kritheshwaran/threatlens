const VARIANTS = {
  primary:
    'bg-accent text-white hover:bg-accent-strong disabled:bg-accent/40',
  secondary:
    'bg-surface2 text-text-primary border border-border hover:border-border-strong disabled:opacity-50',
  ghost:
    'bg-transparent text-text-secondary hover:text-text-primary hover:bg-surface2 disabled:opacity-50',
  danger:
    'bg-malicious/10 text-malicious border border-malicious/30 hover:bg-malicious/20 disabled:opacity-50',
};

const SIZES = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-sm',
};

export default function Button({
  as: Component = 'button',
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}) {
  return (
    <Component
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium
        transition-colors duration-150 disabled:cursor-not-allowed
        ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}