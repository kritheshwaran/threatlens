import { useNavigate } from 'react-router-dom';
import { Menu, Plus } from 'lucide-react';
import Button from '../ui/Button';

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/scanner': 'Scanner',
  '/history': 'Scan History',
  '/analytics': 'Analytics',
  '/settings': 'Settings',
};

export default function Topbar({ onMenuClick, pathname }) {
  const navigate = useNavigate();
  const title =
    PAGE_TITLES[pathname] ||
    (pathname.startsWith('/report') ? 'Scan Result' : 'ThreatLens');

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-bg/95 px-4 backdrop-blur sm:px-6">
      <button
        type="button"
        onClick={onMenuClick}
        className="flex h-9 w-9 items-center justify-center rounded-lg text-text-secondary hover:bg-surface2 hover:text-text-primary lg:hidden"
        aria-label="Toggle navigation"
      >
        <Menu size={18} />
      </button>

      <h1 className="font-display text-base font-semibold text-text-primary">{title}</h1>

      <div className="ml-auto flex items-center gap-3">
        <Button size="sm" onClick={() => navigate('/scanner')}>
          <Plus size={15} strokeWidth={2.25} />
          New Scan
        </Button>
      </div>
    </header>
  );
}