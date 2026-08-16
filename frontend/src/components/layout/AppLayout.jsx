import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-bg font-body text-text-primary">
      <Sidebar open={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <div className="lg:pl-64">
        <Topbar onMenuClick={() => setSidebarOpen((v) => !v)} pathname={location.pathname} />
        <main className="mx-auto max-w-[1400px] px-4 py-6 sm:px-6 lg:py-8 animate-fadeUp">
          <Outlet />
        </main>
      </div>
    </div>
  );
}