import { Routes, Route } from 'react-router-dom';
import './index.css';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import Scanner from './pages/Scanner';
import Report from './pages/Report';
import History from './pages/History';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/report/:id" element={<Report />} />
        <Route path="/history" element={<History />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}

export default App;