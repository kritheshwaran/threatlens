import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { Card, CardBody, Button, ErrorState } from '../components/ui';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setLoading(true);
    try {
      await register(email, password);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-accent-soft text-accent">
            <ShieldCheck size={22} strokeWidth={2.25} />
          </span>
          <h1 className="font-display text-xl font-semibold text-text-primary">Create your account</h1>
          <p className="text-sm text-text-secondary">Start scanning URLs and tracking threats.</p>
        </div>

        <Card>
          <CardBody className="flex flex-col gap-4">
            {error && <ErrorState title="Couldn't create account" description={error} />}

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <label className="text-sm">
                <span className="mb-1.5 block text-xs font-medium text-text-secondary">Email</span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  className="h-10 w-full rounded-lg border border-border bg-surface2 px-3 text-sm text-text-primary
                    focus:border-accent focus:outline-none disabled:opacity-60"
                  placeholder="you@company.com"
                />
              </label>

              <label className="text-sm">
                <span className="mb-1.5 block text-xs font-medium text-text-secondary">Password</span>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  className="h-10 w-full rounded-lg border border-border bg-surface2 px-3 text-sm text-text-primary
                    focus:border-accent focus:outline-none disabled:opacity-60"
                  placeholder="At least 8 characters"
                />
              </label>

              <label className="text-sm">
                <span className="mb-1.5 block text-xs font-medium text-text-secondary">Confirm password</span>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={loading}
                  className="h-10 w-full rounded-lg border border-border bg-surface2 px-3 text-sm text-text-primary
                    focus:border-accent focus:outline-none disabled:opacity-60"
                  placeholder="••••••••"
                />
              </label>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Creating account…' : 'Create account'}
              </Button>
            </form>

            <p className="text-center text-xs text-text-secondary">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-accent hover:text-accent-strong">
                Sign in
              </Link>
            </p>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}