'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

import { api, saveToken } from '../../lib/api';

export default function LoginPage() {
    const router = useRouter();
    const [mode, setMode] = useState<'login' | 'register'>('login');
    const [email, setEmail] = useState('demo@tripwise.app');
    const [password, setPassword] = useState('TripWise@123');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    async function submit(event: FormEvent) {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const data = await api(
                mode === 'login'
                    ? '/auth/login'
                    : '/auth/register',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        email,
                        password,
                    }),
                },
            );

            saveToken(data.token);
            router.replace('/planner');
        } catch (requestError) {
            setError(
                requestError instanceof Error
                    ? requestError.message
                    : 'Authentication failed.',
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <main className="auth-page">
            <div className="card auth-card">
                <p className="eyebrow">TRIPWISE ACCOUNT</p>
                <h1>
                    {mode === 'login'
                        ? 'Welcome back'
                        : 'Create your account'}
                </h1>
                <p>
                    Sign in to keep your trips private and tied to your account.
                </p>

                <form className="form" onSubmit={submit}>
                    <label>
                        Email
                        <input
                            type="email"
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                            required
                        />
                    </label>

                    <label>
                        Password
                        <input
                            type="password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            minLength={6}
                            required
                        />
                    </label>

                    {error && <p className="error">{error}</p>}

                    <button
                        className="button"
                        disabled={loading}
                        type="submit"
                    >
                        {loading
                            ? 'Please wait...'
                            : mode === 'login'
                              ? 'Login'
                              : 'Create account'}
                    </button>
                </form>

                {mode === 'login' && (
                    <div className="demo-box">
                        <strong>Demo credentials</strong>
                        <span>Email: demo@tripwise.app</span>
                        <span>Password: TripWise@123</span>
                    </div>
                )}

                <button
                    className="text-button"
                    type="button"
                    onClick={() => {
                        setMode(
                            mode === 'login'
                                ? 'register'
                                : 'login',
                        );
                        setError('');
                    }}
                >
                    {mode === 'login'
                        ? 'Create a new account'
                        : 'Already have an account? Login'}
                </button>
            </div>
        </main>
    );
}
